"""
统计API - 图表/统计接口
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, List
from app.infrastructure.database import get_db
from app.models.schemas import TrendData, ProjectSummary, ProjectTrends, ContributorsResponse, ContributorInfo, ContributorChartData
from app.services.comment_service import comment_service

router = APIRouter(prefix="/stats", tags=["stats"])

def normalize_project_name(name: str) -> str:
    """
    标准化项目名称
    数据库中使用 owner/repo 格式，所以将 owner_repo 转换为 owner/repo
    """
    if '_' in name and '/' not in name:
        return name.replace('_', '/', 1)
    return name


def get_project_summary_data(db: Session, project: str) -> Dict:
    """获取项目摘要信息
    
    使用 total_stargazers 和 total_forks 字段获取累计总数。
    """
    summary = {
        'project': project.replace('/', '_') if '/' in project else project,
        'repo_name': project,
        'total_stars': 0,
        'total_forks': 0
    }
    
    try:
        # 获取累计总数（使用 total_stargazers 和 total_forks 字段）
        combined_sql = """
            SELECT 
                (SELECT COALESCE(MAX(total_stargazers), 0) FROM stars WHERE project = :project) as total_stars,
                (SELECT COALESCE(MAX(total_forks), 0) FROM forks WHERE project = :project) as total_forks
        """
        result = db.execute(text(combined_sql), {'project': project}).fetchone()
        
        if result:
            summary['total_stars'] = int(result[0]) if result[0] else 0
            summary['total_forks'] = int(result[1]) if result[1] else 0
    except Exception as e:
        print(f"Summary query error: {e}")
    
    return summary


def get_stars_trend_data(db: Session, project: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, List]:
    """获取Stars趋势数据 - 包含每日新增和累计总量
    
    数据库字段说明：
    - stars_count: 每日新增的 star 数量
    - total_stargazers: 项目的最终累计 star 总数（固定值）
    
    累计趋势通过从 total_stargazers 倒推计算得出。
    """
    params = {'project': project}
    
    try:
        # 获取最近100天数据
        sql = """
            SELECT date, stars_count, total_stargazers
            FROM stars 
            WHERE project = :project 
            ORDER BY date DESC 
            LIMIT 100
        """
        results = db.execute(text(sql), params).fetchall()
        # 反转为升序（从早到晚）
        results = list(reversed(results))
    except Exception as e:
        print(f"Stars trend query error: {e}")
        results = []
    
    if not results:
        return {"labels": [], "values": [], "totals": []}
    
    labels = [str(row[0]) for row in results]
    # stars_count 是每日新增值
    values = [int(row[1]) if row[1] else 0 for row in results]
    
    # 获取最终累计总数
    final_total = int(results[-1][2]) if results[-1][2] else 0
    
    # 从最终累计值倒推每天的累计值
    # 最后一天的累计 = final_total
    # 倒数第二天的累计 = final_total - 最后一天的新增
    # 以此类推...
    totals = []
    total_daily_sum = sum(values)
    
    # 计算第一天之前的累计基准
    start_total = max(0, final_total - total_daily_sum)
    
    # 正向累加计算每天的累计值
    cumulative = start_total
    for daily in values:
        cumulative += daily
        totals.append(cumulative)
    
    return {"labels": labels, "values": values, "totals": totals}


def get_forks_trend_data(db: Session, project: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, List]:
    """获取Forks趋势数据 - 包含每日新增和累计总量
    
    数据库字段说明：
    - forks_count: 每日新增的 fork 数量
    - total_forks: 项目的最终累计 fork 总数（固定值）
    
    累计趋势通过从 total_forks 倒推计算得出。
    """
    params = {'project': project}
    
    try:
        # 获取最近100天数据
        sql = """
            SELECT date, forks_count, total_forks
            FROM forks 
            WHERE project = :project 
            ORDER BY date DESC 
            LIMIT 100
        """
        results = db.execute(text(sql), params).fetchall()
        # 反转为升序（从早到晚）
        results = list(reversed(results))
    except Exception as e:
        print(f"Forks trend query error: {e}")
        results = []
    
    if not results:
        return {"labels": [], "values": [], "totals": []}
    
    labels = [str(row[0]) for row in results]
    # forks_count 是每日新增值
    values = [int(row[1]) if row[1] else 0 for row in results]
    
    # 获取最终累计总数
    final_total = int(results[-1][2]) if results[-1][2] else 0
    
    # 从最终累计值倒推每天的累计值
    # 最后一天的累计 = final_total
    # 倒数第二天的累计 = final_total - 最后一天的新增
    # 以此类推...
    totals = []
    total_daily_sum = sum(values)
    
    # 计算第一天之前的累计基准
    start_total = max(0, final_total - total_daily_sum)
    
    # 正向累加计算每天的累计值
    cumulative = start_total
    for daily in values:
        cumulative += daily
        totals.append(cumulative)
    
    return {"labels": labels, "values": values, "totals": totals}


@router.get("/project/summary", response_model=ProjectSummary)
async def get_project_summary(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）"),
    db: Session = Depends(get_db)
):
    """获取项目摘要信息"""
    project_key = normalize_project_name(project)
    summary = get_project_summary_data(db, project_key)
    return ProjectSummary(**summary)


@router.get("/stars/trend", response_model=TrendData)
async def get_stars_trend(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_db)
):
    """获取项目Stars趋势图数据"""
    project_key = normalize_project_name(project)
    result = get_stars_trend_data(db, project_key, start_date, end_date)
    return TrendData(**result)


@router.get("/forks/trend", response_model=TrendData)
async def get_forks_trend(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_db)
):
    """获取项目Forks趋势图数据"""
    project_key = normalize_project_name(project)
    result = get_forks_trend_data(db, project_key, start_date, end_date)
    return TrendData(**result)


@router.get("/project/trends", response_model=ProjectTrends)
async def get_project_trends(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_db)
):
    """获取项目趋势数据 - Stars 和 Forks（每日新增 + 累计总量）"""
    project_key = normalize_project_name(project)
    
    summary = get_project_summary_data(db, project_key)
    stars_trend = get_stars_trend_data(db, project_key, start_date, end_date)
    forks_trend = get_forks_trend_data(db, project_key, start_date, end_date)
    
    return ProjectTrends(
        summary=ProjectSummary(**summary),
        stars_trend=TrendData(**stars_trend),
        forks_trend=TrendData(**forks_trend)
    )


# ========== 活跃贡献者统计接口 ==========

def get_commit_contributors(db: Session, project: str, top_n: int = 10) -> Dict:
    """
    从 top300_2022_2023 表获取项目的 commit 贡献者统计
    
    Args:
        db: 数据库会话
        project: 项目名称 (owner/repo 格式)
        top_n: 返回 Top N 贡献者
        
    Returns:
        {
            "total_contributors": int,
            "total_commits": int,
            "contributors": [
                {"username": str, "commit_count": int, "percentage": float, "github_url": str}
            ]
        }
    """
    # 转换项目名格式
    if '_' in project and '/' not in project:
        repo_name = project.replace('_', '/', 1)
    else:
        repo_name = project
    
    try:
        # 统计每个用户的 commit 数量（基于 PushEvent）
        sql = """
            SELECT actor_login, COUNT(*) as commit_count
            FROM top300_2022_2023 
            WHERE repo_name = :repo_name 
              AND type = 'PushEvent'
              AND actor_login IS NOT NULL
              AND actor_login != ''
            GROUP BY actor_login
            ORDER BY commit_count DESC
        """
        results = db.execute(text(sql), {'repo_name': repo_name}).fetchall()
        
        if not results:
            return {
                "total_contributors": 0,
                "total_commits": 0,
                "contributors": []
            }
        
        # 计算总 commit 数
        total_commits = sum(row[1] for row in results)
        total_contributors = len(results)
        
        # 取 Top N
        contributors = []
        for username, commit_count in results[:top_n]:
            percentage = round(commit_count / total_commits * 100, 2) if total_commits > 0 else 0
            contributors.append({
                "username": username,
                "commit_count": commit_count,
                "comment_count": commit_count,  # 兼容旧字段
                "percentage": percentage,
                "github_url": f"https://github.com/{username}"
            })
        
        return {
            "total_contributors": total_contributors,
            "total_commits": total_commits,
            "total_comments": total_commits,  # 兼容旧字段
            "contributors": contributors
        }
        
    except Exception as e:
        print(f"获取 commit 贡献者失败: {e}")
        return {
            "total_contributors": 0,
            "total_commits": 0,
            "contributors": []
        }


@router.get("/contributors", response_model=ContributorsResponse)
async def get_contributors(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）"),
    top_n: int = Query(10, ge=1, le=50, description="返回 Top N 活跃贡献者"),
    db: Session = Depends(get_db)
):
    """
    获取项目活跃贡献者统计（基于 commit 数据）
    
    返回按 commit 数量排序的贡献者列表，包含 GitHub 个人主页链接
    """
    project_key = normalize_project_name(project)
    result = get_commit_contributors(db, project_key, top_n)
    
    contributors = [ContributorInfo(**c) for c in result["contributors"]]
    
    return ContributorsResponse(
        total_contributors=result["total_contributors"],
        total_commits=result["total_commits"],
        total_comments=result.get("total_comments", 0),
        contributors=contributors
    )


@router.get("/contributors/chart", response_model=ContributorChartData)
async def get_contributors_chart(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）"),
    top_n: int = Query(10, ge=1, le=20, description="返回 Top N 活跃贡献者"),
    db: Session = Depends(get_db)
):
    """获取活跃贡献者饼图数据（基于 commit）"""
    project_key = normalize_project_name(project)
    result = get_commit_contributors(db, project_key, top_n)
    
    labels = [c["username"] for c in result["contributors"]]
    values = [c["commit_count"] for c in result["contributors"]]
    
    # 添加"其他"类别
    if result["total_contributors"] > top_n:
        other_count = result["total_commits"] - sum(values)
        if other_count > 0:
            labels.append("其他")
            values.append(other_count)
    
    return ContributorChartData(labels=labels, values=values)
