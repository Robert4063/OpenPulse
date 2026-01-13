"""
健康度评估 API
从预计算的 health_scores.json 文件读取数据，快速响应
"""
import json
import os
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/health", tags=["health"])

# 健康度评分缓存
_health_cache = None
_cache_load_time = None

# JSON 文件路径
HEALTH_SCORES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'health_scores.json')


def load_health_scores():
    """加载预计算的健康度评分"""
    global _health_cache, _cache_load_time
    
    try:
        # 检查文件修改时间，如果文件更新了就重新加载
        if os.path.exists(HEALTH_SCORES_FILE):
            file_mtime = os.path.getmtime(HEALTH_SCORES_FILE)
            if _cache_load_time is None or file_mtime > _cache_load_time:
                with open(HEALTH_SCORES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    _health_cache = data.get('scores', {})
                    _cache_load_time = file_mtime
                    print(f"[Health] 已加载 {len(_health_cache)} 个项目的健康度评分")
        return _health_cache or {}
    except Exception as e:
        print(f"[Health] 加载健康度评分失败: {e}")
        return {}


def normalize_project_name(name: str) -> str:
    """标准化项目名称为 owner_repo 格式"""
    if '/' in name:
        return name.replace('/', '_')
    return name


def get_repo_name(name: str) -> str:
    """获取 owner/repo 格式"""
    if '_' in name and '/' not in name:
        return name.replace('_', '/', 1)
    return name


@router.get("/score")
async def get_health_score(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）")
):
    """
    获取项目健康度评分（从预计算数据中读取）
    
    返回包含以下信息的健康度评估结果：
    - 最终得分 (0-100)
    - 健康等级 (A/B/C/D/E)
    - 四个维度的详细得分
    """
    project_key = normalize_project_name(project)
    
    # 从缓存读取
    health_scores = load_health_scores()
    
    if project_key in health_scores:
        data = health_scores[project_key]
        
        # 如果有错误标记，返回默认值
        if data.get('error'):
            return {
                'project': project_key,
                'repo_name': get_repo_name(project_key),
                'final_score': 0,
                'grade': 'N/A',
                'grade_label': '无数据',
                'grade_color': '#6b7280',
                'weights': {
                    'growth': 0.2,
                    'activity': 0.4,
                    'contribution': 0.2,
                    'code': 0.2
                },
                'dimensions': {
                    'growth': {'name': '关注度增长', 'weight': '20%', 'score': 0, 'details': {}},
                    'activity': {'name': '开发活跃度', 'weight': '40%', 'score': 0, 'details': {}},
                    'contribution': {'name': '社区贡献度', 'weight': '20%', 'score': 0, 'details': {}},
                    'code': {'name': '代码健康度', 'weight': '20%', 'score': 0, 'details': {}}
                },
                'calculated_at': datetime.now().isoformat()
            }
        
        # 返回预计算的数据
        return {
            'project': data['project'],
            'repo_name': data['repo_name'],
            'final_score': data['final_score'],
            'grade': data['grade'],
            'grade_label': data['grade_label'],
            'grade_color': data['grade_color'],
            'weights': {
                'growth': 0.2,
                'activity': 0.4,
                'contribution': 0.2,
                'code': 0.2
            },
            'dimensions': data.get('dimensions', {
                'growth': {'name': '关注度增长', 'weight': '20%', 'score': 0, 'details': {}},
                'activity': {'name': '开发活跃度', 'weight': '40%', 'score': 0, 'details': {}},
                'contribution': {'name': '社区贡献度', 'weight': '20%', 'score': 0, 'details': {}},
                'code': {'name': '代码健康度', 'weight': '20%', 'score': 0, 'details': {}}
            }),
            'calculated_at': data.get('calculated_at', datetime.now().isoformat())
        }
    
    # 项目不在预计算列表中
    return {
        'project': project_key,
        'repo_name': get_repo_name(project_key),
        'final_score': 0,
        'grade': 'N/A',
        'grade_label': '未收录',
        'grade_color': '#6b7280',
        'weights': {
            'growth': 0.2,
            'activity': 0.4,
            'contribution': 0.2,
            'code': 0.2
        },
        'dimensions': {
            'growth': {'name': '关注度增长', 'weight': '20%', 'score': 0, 'details': {}},
            'activity': {'name': '开发活跃度', 'weight': '40%', 'score': 0, 'details': {}},
            'contribution': {'name': '社区贡献度', 'weight': '20%', 'score': 0, 'details': {}},
            'code': {'name': '代码健康度', 'weight': '20%', 'score': 0, 'details': {}}
        },
        'calculated_at': datetime.now().isoformat()
    }


@router.get("/summary")
async def get_health_summary(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）")
):
    """
    获取项目健康度评分摘要（简化版本）
    """
    project_key = normalize_project_name(project)
    
    # 从缓存读取
    health_scores = load_health_scores()
    
    if project_key in health_scores:
        data = health_scores[project_key]
        dims = data.get('dimensions', {})
        
        return {
            'project': data['project'],
            'repo_name': data['repo_name'],
            'final_score': data['final_score'],
            'grade': data['grade'],
            'grade_label': data['grade_label'],
            'grade_color': data['grade_color'],
            'growth_score': dims.get('growth', {}).get('score', 0),
            'activity_score': dims.get('activity', {}).get('score', 0),
            'contribution_score': dims.get('contribution', {}).get('score', 0),
            'code_score': dims.get('code', {}).get('score', 0)
        }
    
    # 项目不在预计算列表中
    return {
        'project': project_key,
        'repo_name': get_repo_name(project_key),
        'final_score': 0,
        'grade': 'N/A',
        'grade_label': '未收录',
        'grade_color': '#6b7280',
        'growth_score': 0,
        'activity_score': 0,
        'contribution_score': 0,
        'code_score': 0
    }


@router.get("/all")
async def get_all_health_scores():
    """获取所有项目的健康度评分（用于排行榜等）"""
    health_scores = load_health_scores()
    
    # 转换为列表并按分数排序
    scores_list = []
    for key, data in health_scores.items():
        if not data.get('error'):
            scores_list.append({
                'project': data['project'],
                'repo_name': data['repo_name'],
                'final_score': data['final_score'],
                'grade': data['grade'],
                'grade_label': data['grade_label'],
                'grade_color': data['grade_color']
            })
    
    # 按分数降序排序
    scores_list.sort(key=lambda x: x['final_score'], reverse=True)
    
    return {
        'total': len(scores_list),
        'scores': scores_list
    }


@router.get("/similar")
async def get_similar_projects(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）"),
    limit: int = Query(5, ge=1, le=20, description="返回相似项目的数量")
):
    """
    获取与指定项目健康度相似的项目
    
    返回健康度分数接近的其他项目列表
    """
    project_key = normalize_project_name(project)
    health_scores = load_health_scores()
    
    # 获取当前项目的分数
    if project_key not in health_scores:
        return {
            'project': project_key,
            'similar_projects': [],
            'message': '项目未收录'
        }
    
    current_score = health_scores[project_key].get('final_score', 0)
    current_grade = health_scores[project_key].get('grade', 'N/A')
    
    # 计算所有项目与当前项目的分数差距
    similar_projects = []
    for key, data in health_scores.items():
        if key == project_key or data.get('error'):
            continue
        
        score_diff = abs(data['final_score'] - current_score)
        similar_projects.append({
            'project': data['project'],
            'repo_name': data['repo_name'],
            'final_score': data['final_score'],
            'grade': data['grade'],
            'grade_label': data['grade_label'],
            'grade_color': data['grade_color'],
            'score_diff': round(score_diff, 2)
        })
    
    # 按分数差距排序，取最接近的项目
    similar_projects.sort(key=lambda x: x['score_diff'])
    
    return {
        'project': project_key,
        'current_score': current_score,
        'current_grade': current_grade,
        'similar_projects': similar_projects[:limit]
    }


@router.get("/languages")
async def get_project_languages(
    project: str = Query(..., description="项目名称（格式：owner/repo 或 owner_repo）")
):
    """
    获取项目使用的编程语言信息
    
    从 GitHub API 获取项目的语言统计信息
    """
    import httpx
    
    # 转换项目名格式
    if '_' in project and '/' not in project:
        repo_name = project.replace('_', '/', 1)
    else:
        repo_name = project
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 调用 GitHub API 获取语言信息
            response = await client.get(
                f"https://api.github.com/repos/{repo_name}/languages",
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "OpenPulse-HealthAnalyzer"
                }
            )
            
            if response.status_code == 200:
                languages_data = response.json()
                
                # 计算总字节数和百分比
                total_bytes = sum(languages_data.values())
                
                languages = []
                for lang, bytes_count in sorted(languages_data.items(), key=lambda x: x[1], reverse=True):
                    percentage = round((bytes_count / total_bytes) * 100, 2) if total_bytes > 0 else 0
                    languages.append({
                        'name': lang,
                        'bytes': bytes_count,
                        'percentage': percentage,
                        'color': get_language_color(lang)
                    })
                
                return {
                    'project': project,
                    'repo_name': repo_name,
                    'total_bytes': total_bytes,
                    'languages': languages
                }
            elif response.status_code == 404:
                return {
                    'project': project,
                    'repo_name': repo_name,
                    'total_bytes': 0,
                    'languages': [],
                    'error': '项目不存在或无法访问'
                }
            else:
                return {
                    'project': project,
                    'repo_name': repo_name,
                    'total_bytes': 0,
                    'languages': [],
                    'error': f'GitHub API 错误: {response.status_code}'
                }
                
    except Exception as e:
        return {
            'project': project,
            'repo_name': repo_name,
            'total_bytes': 0,
            'languages': [],
            'error': str(e)
        }


def get_language_color(language: str) -> str:
    """获取编程语言对应的颜色"""
    colors = {
        'JavaScript': '#f7df1e',
        'TypeScript': '#3178c6',
        'Python': '#3572A5',
        'Java': '#b07219',
        'C': '#555555',
        'C++': '#f34b7d',
        'C#': '#239120',
        'Go': '#00ADD8',
        'Rust': '#dea584',
        'Ruby': '#701516',
        'PHP': '#4F5D95',
        'Swift': '#F05138',
        'Kotlin': '#A97BFF',
        'Scala': '#c22d40',
        'HTML': '#e34c26',
        'CSS': '#1572B6',
        'SCSS': '#c6538c',
        'Shell': '#89e051',
        'Dockerfile': '#384d54',
        'Makefile': '#427819',
        'Vue': '#4FC08D',
        'Dart': '#00B4AB',
        'R': '#198CE7',
        'Lua': '#000080',
        'Perl': '#0298c3',
        'Haskell': '#5e5086',
        'Elixir': '#6e4a7e',
        'Clojure': '#db5855',
        'Objective-C': '#438eff',
        'PowerShell': '#012456',
        'Vim script': '#199f4b',
        'Assembly': '#6E4C13',
        'Julia': '#a270ba',
        'TeX': '#3D6117',
        'CoffeeScript': '#244776',
        'Groovy': '#4298b8',
        'Jupyter Notebook': '#DA5B0B',
        'MATLAB': '#e16737',
        'Fortran': '#4d41b1',
        'Elm': '#60B5CC',
        'OCaml': '#3be133',
        'F#': '#b845fc',
        'Erlang': '#B83998',
        'Nix': '#7e7eff',
        'Zig': '#ec915c',
        'Svelte': '#ff3e00',
        'Astro': '#ff5a03',
        'MDX': '#fcb32c'
    }
    return colors.get(language, '#6b7280')