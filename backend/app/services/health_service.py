"""
项目健康度评估服务
基于 PHAM (Project Health Assessment Model) v2.0
优化版：合并查询、减少数据库访问次数
"""
import math
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import time


class HealthService:
    """项目健康度计算服务"""
    
    # 权重配置
    WEIGHT_GROWTH = 0.2       # 关注度增长权重
    WEIGHT_ACTIVITY = 0.4    # 活跃度权重
    WEIGHT_CONTRIB = 0.2     # 贡献度权重
    WEIGHT_CODE = 0.2        # 代码健康度权重
    
    # OpenDigger 活跃度归一化系数
    OPENDIGGER_FACTOR = 10
    
    # 缓存 top300 数据的过期时间（秒）
    TOP300_CACHE_TTL = 3600  # 1小时
    
    # 基准日期配置（使用2023年3月作为"当前"时间点）
    REFERENCE_DATE = '2023-03-31'           # 基准日期
    REFERENCE_MONTH_START = '2023-03-01'    # 本月开始
    REFERENCE_PREV_3M_START = '2022-12-01'  # 前3个月开始
    REFERENCE_LAST_WEEK = '2023-03-24'      # 最近一周开始（3月31日-7天）
    
    # 类级别缓存
    _top300_cache = {}
    _top300_cache_time = {}
    
    def __init__(self, db: Session):
        self.db = db
    
    def normalize_project_name(self, name: str) -> str:
        """标准化项目名称：owner/repo -> owner_repo（用于返回值）"""
        if '/' in name:
            return name.replace('/', '_')
        return name
    
    def get_repo_name(self, name: str) -> str:
        """获取仓库名称格式：owner_repo -> owner/repo（用于数据库查询）"""
        if '_' in name and '/' not in name:
            return name.replace('_', '/', 1)
        return name
    
    def get_star_fork_data_combined(self, project: str) -> Tuple[Dict, Dict]:
        """
        合并获取 Star 和 Fork 数据（减少查询次数）
        使用单个查询获取所有必要数据
        """
        star_result = {
            'star_current_month': 0,
            'star_avg_prev_3m': 0.0
        }
        fork_result = {
            'fork_current_month': 0,
            'fork_avg_prev_3m': 0.0
        }
        
        # 数据库中使用 owner/repo 格式
        repo_name = self.get_repo_name(project)
        
        try:
            # 合并查询：一次获取所有 star 和 fork 统计数据
            # 使用固定的基准日期（2023年3月）而非当前日期
            combined_sql = """
                SELECT 
                    -- Star 本月（2023年3月）
                    (SELECT COALESCE(SUM(stars_count), 0) FROM stars 
                     WHERE project = :project 
                     AND date >= :month_start AND date <= :ref_date) as star_current,
                    -- Star 前3月平均（2022年12月-2023年2月）
                    (SELECT COALESCE(AVG(monthly_total), 0) FROM (
                        SELECT SUM(stars_count) as monthly_total
                        FROM stars WHERE project = :project 
                        AND date >= :prev_3m_start
                        AND date < :month_start
                        GROUP BY DATE_FORMAT(date, '%Y-%m')
                    ) as star_monthly) as star_avg_3m,
                    -- Fork 本月（2023年3月）
                    (SELECT COALESCE(SUM(forks_count), 0) FROM forks 
                     WHERE project = :project 
                     AND date >= :month_start AND date <= :ref_date) as fork_current,
                    -- Fork 前3月平均（2022年12月-2023年2月）
                    (SELECT COALESCE(AVG(monthly_total), 0) FROM (
                        SELECT SUM(forks_count) as monthly_total
                        FROM forks WHERE project = :project 
                        AND date >= :prev_3m_start
                        AND date < :month_start
                        GROUP BY DATE_FORMAT(date, '%Y-%m')
                    ) as fork_monthly) as fork_avg_3m
            """
            row = self.db.execute(text(combined_sql), {
                'project': repo_name,
                'ref_date': self.REFERENCE_DATE,
                'month_start': self.REFERENCE_MONTH_START,
                'prev_3m_start': self.REFERENCE_PREV_3M_START
            }).fetchone()
            
            if row:
                star_result['star_current_month'] = int(row[0]) if row[0] else 0
                star_result['star_avg_prev_3m'] = float(row[1]) if row[1] else 0.0
                fork_result['fork_current_month'] = int(row[2]) if row[2] else 0
                fork_result['fork_avg_prev_3m'] = float(row[3]) if row[3] else 0.0
                
        except Exception as e:
            print(f"获取 Star/Fork 数据失败: {e}")
        
        return star_result, fork_result
    
    def get_commit_pr_data_combined(self, project: str) -> Tuple[Dict, Dict]:
        """
        合并获取 Commit 和 PR 数据（减少查询次数）
        """
        commit_result = {
            'commit_avg_last_week': 0.0,
            'commit_avg_month': 0.0
        }
        pr_result = {
            'pr_avg_last_week': 0.0,
            'pr_avg_month': 0.0
        }
        
        # 数据库中使用 owner/repo 格式
        repo_name = self.get_repo_name(project)
        
        try:
            # 合并查询：一次获取所有 commit 和 pr 统计数据
            # 使用固定的基准日期（2023年3月）而非当前日期
            combined_sql = """
                SELECT 
                    -- Commit 最近一周平均（2023-03-24 到 2023-03-31）
                    (SELECT COALESCE(AVG(commit_count), 0) FROM commit_activity 
                     WHERE project = :project AND date >= :last_week AND date <= :ref_date) as commit_week,
                    -- Commit 本月平均（2023年3月）
                    (SELECT COALESCE(AVG(commit_count), 0) FROM commit_activity 
                     WHERE project = :project AND date >= :month_start AND date <= :ref_date) as commit_month,
                    -- PR 最近一周平均（2023-03-24 到 2023-03-31）
                    (SELECT COALESCE(AVG(pr_count), 0) FROM pr_daily 
                     WHERE project = :project AND date >= :last_week AND date <= :ref_date) as pr_week,
                    -- PR 本月平均（2023年3月）
                    (SELECT COALESCE(AVG(pr_count), 0) FROM pr_daily 
                     WHERE project = :project AND date >= :month_start AND date <= :ref_date) as pr_month
            """
            row = self.db.execute(text(combined_sql), {
                'project': repo_name,
                'ref_date': self.REFERENCE_DATE,
                'month_start': self.REFERENCE_MONTH_START,
                'last_week': self.REFERENCE_LAST_WEEK
            }).fetchone()
            
            if row:
                commit_result['commit_avg_last_week'] = float(row[0]) if row[0] else 0.0
                commit_result['commit_avg_month'] = float(row[1]) if row[1] else 0.0
                pr_result['pr_avg_last_week'] = float(row[2]) if row[2] else 0.0
                pr_result['pr_avg_month'] = float(row[3]) if row[3] else 0.0
                
        except Exception as e:
            print(f"获取 Commit/PR 数据失败: {e}")
        
        return commit_result, pr_result
    
    def get_top300_data(self, project: str) -> Dict:
        """
        从 top300_2022_2023 表获取数据（带缓存）
        - opendigger_activity: OpenDigger Activity 指标
        - pull_additions: 代码添加行数
        - pull_deletions: 代码删除行数
        """
        repo_name = project.replace('_', '/', 1) if '_' in project else project
        
        # 检查缓存
        cache_key = repo_name
        current_time = time.time()
        if cache_key in self._top300_cache:
            cache_time = self._top300_cache_time.get(cache_key, 0)
            if current_time - cache_time < self.TOP300_CACHE_TTL:
                return self._top300_cache[cache_key]
        
        result = {
            'opendigger_activity': 0.0,
            'pull_additions': 0,
            'pull_deletions': 0
        }
        
        try:
            # 分两步查询：1. 获取代码变动数据 2. 获取活跃度指标
            # 代码变动数据只来自 PullRequestEvent
            code_sql = """
                SELECT 
                    COALESCE(SUM(pull_additions), 0) as total_additions,
                    COALESCE(SUM(pull_deletions), 0) as total_deletions
                FROM top300_2022_2023 
                WHERE repo_name = :repo_name AND type = 'PullRequestEvent'
            """
            code_row = self.db.execute(text(code_sql), {'repo_name': repo_name}).fetchone()
            
            if code_row:
                result['pull_additions'] = int(code_row[0]) if code_row[0] else 0
                result['pull_deletions'] = int(code_row[1]) if code_row[1] else 0
            
            # 活跃度指标：统计各类事件数量
            activity_sql = """
                SELECT 
                    COUNT(DISTINCT CASE WHEN type = 'PushEvent' THEN id END) as push_count,
                    COUNT(DISTINCT CASE WHEN type = 'PullRequestEvent' THEN id END) as pr_count,
                    COUNT(DISTINCT CASE WHEN type = 'IssuesEvent' THEN id END) as issue_count,
                    COUNT(DISTINCT actor_id) as contributor_count
                FROM top300_2022_2023 
                WHERE repo_name = :repo_name
            """
            row = self.db.execute(text(activity_sql), {'repo_name': repo_name}).fetchone()
            
            if row:
                push_count = int(row[0]) if row[0] else 0
                pr_count = int(row[1]) if row[1] else 0
                issue_count = int(row[2]) if row[2] else 0
                contributor_count = int(row[3]) if row[3] else 0
                
                # 归一化处理
                normalized_push = min(push_count / 1000, 1) * 3
                normalized_pr = min(pr_count / 500, 1) * 4
                normalized_issue = min(issue_count / 200, 1) * 2
                normalized_contributor = min(contributor_count / 100, 1) * 1
                
                result['opendigger_activity'] = normalized_push + normalized_pr + normalized_issue + normalized_contributor
            
            # 更新缓存
            self._top300_cache[cache_key] = result
            self._top300_cache_time[cache_key] = current_time
            
        except Exception as e:
            print(f"获取 top300 数据失败: {e}")
        
        return result
    
    def calculate_growth_score(self, star_data: Dict, fork_data: Dict) -> Dict:
        """计算关注度增长得分 (Growth) - 权重 20%"""
        s_cur = star_data['star_current_month']
        s_avg = star_data['star_avg_prev_3m']
        x = (s_cur / (s_avg + 1)) * 100
        score_x = min(x, 200) / 2
        
        f_cur = fork_data['fork_current_month']
        f_avg = fork_data['fork_avg_prev_3m']
        y = (f_cur / (f_avg + 1)) * 100
        score_y = min(y, 200) / 2
        
        score_growth = 0.5 * score_x + 0.5 * score_y
        
        return {
            'score': round(score_growth, 2),
            'star_score': round(score_x, 2),
            'fork_score': round(score_y, 2),
            'details': {
                'star_current_month': s_cur,
                'star_avg_prev_3m': round(s_avg, 2),
                'fork_current_month': f_cur,
                'fork_avg_prev_3m': round(f_avg, 2)
            }
        }
    
    def calculate_activity_score(self, commit_data: Dict, opendigger_activity: float) -> Dict:
        """计算活跃度得分 (Activity) - 权重 40%"""
        c_last = commit_data['commit_avg_last_week']
        c_month = commit_data['commit_avg_month']
        c_ratio = (c_last + 1) / (c_month + 1)
        score_z = max(0, min(100, 50 + (c_ratio - 1) * 50))
        
        score_m = min(100, opendigger_activity * self.OPENDIGGER_FACTOR)
        score_activity = 0.3 * score_z + 0.7 * score_m
        
        return {
            'score': round(score_activity, 2),
            'commit_trend_score': round(score_z, 2),
            'opendigger_score': round(score_m, 2),
            'details': {
                'commit_avg_last_week': round(c_last, 2),
                'commit_avg_month': round(c_month, 2),
                'commit_ratio': round(c_ratio, 2),
                'opendigger_activity': round(opendigger_activity, 2)
            }
        }
    
    def calculate_contribution_score(self, pr_data: Dict) -> Dict:
        """计算贡献度得分 (Contribution) - 权重 20%"""
        p_last = pr_data['pr_avg_last_week']
        p_month = pr_data['pr_avg_month']
        p_ratio = (p_last + 1) / (p_month + 1)
        score_contrib = max(0, min(100, 50 + (p_ratio - 1) * 50))
        
        return {
            'score': round(score_contrib, 2),
            'details': {
                'pr_avg_last_week': round(p_last, 2),
                'pr_avg_month': round(p_month, 2),
                'pr_ratio': round(p_ratio, 2)
            }
        }
    
    def calculate_code_score(self, pull_additions: int, pull_deletions: int) -> Dict:
        """计算代码健康度得分 (Code Churn) - 权重 20%"""
        total_churn = pull_additions + pull_deletions
        if total_churn > 0:
            score_code = min(100, 20 * math.log10(total_churn + 1))
        else:
            score_code = 0
        
        return {
            'score': round(score_code, 2),
            'details': {
                'pull_additions': pull_additions,
                'pull_deletions': pull_deletions,
                'total_churn': total_churn
            }
        }
    
    def calculate_health_score(self, project: str) -> Dict:
        """
        计算项目健康度评分（主入口）
        优化：将10次查询减少到3次
        """
        project_key = self.normalize_project_name(project)
        
        # 优化：合并查询，从10次减少到3次
        star_data, fork_data = self.get_star_fork_data_combined(project_key)
        commit_data, pr_data = self.get_commit_pr_data_combined(project_key)
        top300_data = self.get_top300_data(project_key)
        
        # 计算各维度得分
        growth_result = self.calculate_growth_score(star_data, fork_data)
        activity_result = self.calculate_activity_score(commit_data, top300_data['opendigger_activity'])
        contribution_result = self.calculate_contribution_score(pr_data)
        code_result = self.calculate_code_score(top300_data['pull_additions'], top300_data['pull_deletions'])
        
        # 计算最终得分
        final_score = (
            self.WEIGHT_GROWTH * growth_result['score'] +
            self.WEIGHT_ACTIVITY * activity_result['score'] +
            self.WEIGHT_CONTRIB * contribution_result['score'] +
            self.WEIGHT_CODE * code_result['score']
        )
        
        # 确定健康等级
        if final_score >= 80:
            grade, grade_label, grade_color = 'A', '优秀', '#22c55e'
        elif final_score >= 60:
            grade, grade_label, grade_color = 'B', '良好', '#3b82f6'
        elif final_score >= 40:
            grade, grade_label, grade_color = 'C', '一般', '#eab308'
        elif final_score >= 20:
            grade, grade_label, grade_color = 'D', '较差', '#f97316'
        else:
            grade, grade_label, grade_color = 'E', '危险', '#ef4444'
        
        return {
            'project': project_key,
            'repo_name': project_key.replace('_', '/', 1) if '_' in project_key else project_key,
            'final_score': round(final_score, 2),
            'grade': grade,
            'grade_label': grade_label,
            'grade_color': grade_color,
            'weights': {
                'growth': self.WEIGHT_GROWTH,
                'activity': self.WEIGHT_ACTIVITY,
                'contribution': self.WEIGHT_CONTRIB,
                'code': self.WEIGHT_CODE
            },
            'dimensions': {
                'growth': {
                    'name': '关注度增长',
                    'weight': f'{int(self.WEIGHT_GROWTH * 100)}%',
                    'score': growth_result['score'],
                    'star_score': growth_result['star_score'],
                    'fork_score': growth_result['fork_score'],
                    'details': growth_result['details']
                },
                'activity': {
                    'name': '开发活跃度',
                    'weight': f'{int(self.WEIGHT_ACTIVITY * 100)}%',
                    'score': activity_result['score'],
                    'commit_trend_score': activity_result['commit_trend_score'],
                    'opendigger_score': activity_result['opendigger_score'],
                    'details': activity_result['details']
                },
                'contribution': {
                    'name': '社区贡献度',
                    'weight': f'{int(self.WEIGHT_CONTRIB * 100)}%',
                    'score': contribution_result['score'],
                    'details': contribution_result['details']
                },
                'code': {
                    'name': '代码健康度',
                    'weight': f'{int(self.WEIGHT_CODE * 100)}%',
                    'score': code_result['score'],
                    'details': code_result['details']
                }
            },
            'calculated_at': datetime.now().isoformat(),
            'reference_date': self.REFERENCE_DATE,
            'reference_period': '基准时间: 2023年3月'
        }


def get_health_service(db: Session) -> HealthService:
    """获取健康度服务实例"""
    return HealthService(db)
