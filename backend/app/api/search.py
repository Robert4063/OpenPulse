"""
搜索API - 搜索类接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict
from app.infrastructure.database import get_db
from app.models.schemas import ProjectInfo, ProjectSearchResponse

router = APIRouter(prefix="/search", tags=["search"])


def search_projects_data(
    db: Session,
    keyword: Optional[str] = None,
    stars_min: Optional[int] = None,
    stars_max: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
) -> tuple[List[Dict], int]:
    """
    搜索项目
    从stars表中获取项目列表，聚合最新的stars/forks数据
    """
    # 构建WHERE条件
    conditions = []
    params = {}
    
    if keyword:
        conditions.append("s.project LIKE :keyword")
        params['keyword'] = f"%{keyword}%"
    
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    having_clause = ""
    having_conditions = []
    
    if stars_min is not None:
        having_conditions.append("latest_stars >= :stars_min")
        params['stars_min'] = stars_min
    
    if stars_max is not None:
        having_conditions.append("latest_stars <= :stars_max")
        params['stars_max'] = stars_max
    
    if having_conditions:
        having_clause = " HAVING " + " AND ".join(having_conditions)
    
    # 查询总数
    count_sql = f"""
        SELECT COUNT(*) FROM (
            SELECT s.project
            FROM stars s
            {where_clause}
            GROUP BY s.project
            {having_clause}
        ) as subquery
    """
    
    try:
        count_result = db.execute(text(count_sql), params).fetchone()
        total = count_result[0] if count_result else 0
    except Exception as e:
        print(f"Count query error: {e}")
        total = 0
    
    # 查询项目列表
    query_sql = f"""
        SELECT 
            s.project,
            MAX(s.total_stargazers) as latest_stars,
            MAX(s.date) as latest_date
        FROM stars s
        {where_clause}
        GROUP BY s.project
        {having_clause}
        ORDER BY latest_stars DESC
        LIMIT :limit OFFSET :offset
    """
    
    params['limit'] = limit
    params['offset'] = offset
    
    try:
        results = db.execute(text(query_sql), params).fetchall()
    except Exception as e:
        print(f"Query error: {e}")
        results = []
    
    # 获取forks数据
    items = []
    for row in results:
        project = row[0]
        stars = row[1] or 0
        
        # 获取该项目的forks数
        try:
            forks_result = db.execute(
                text("SELECT MAX(total_fork) FROM forks WHERE project = :project"),
                {'project': project}
            ).fetchone()
            forks = forks_result[0] if forks_result and forks_result[0] else 0
        except:
            forks = 0
        
        # 转换项目名格式 owner_repo -> owner/repo
        repo_name = project.replace('_', '/', 1) if '_' in project else project
        
        items.append({
            'id': hash(project) % 100000,
            'repo_name': repo_name,
            'project_key': project,
            'stars': stars,
            'forks': forks,
            'updated_at': row[2]
        })
    
    return items, total


def get_all_projects_data(db: Session, limit: int = 100) -> List[str]:
    """获取所有项目列表"""
    try:
        results = db.execute(
            text("SELECT DISTINCT project FROM stars ORDER BY project LIMIT :limit"),
            {'limit': limit}
        ).fetchall()
        return [row[0] for row in results]
    except Exception as e:
        print(f"Get projects error: {e}")
        return []


@router.get("/projects", response_model=ProjectSearchResponse)
async def search_projects(
    keyword: Optional[str] = Query(None, description="项目名称关键词"),
    stars_min: Optional[int] = Query(None, description="最小stars数"),
    stars_max: Optional[int] = Query(None, description="最大stars数"),
    limit: int = Query(50, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """搜索项目"""
    items, total = search_projects_data(
        db,
        keyword=keyword,
        stars_min=stars_min,
        stars_max=stars_max,
        limit=limit,
        offset=offset
    )
    
    project_items = [ProjectInfo(**item) for item in items]
    
    return ProjectSearchResponse(
        total=total,
        items=project_items
    )


@router.get("/projects/list", response_model=List[str])
async def get_project_list(
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取所有项目名称列表"""
    return get_all_projects_data(db, limit=limit)


@router.get("/projects/top", response_model=ProjectSearchResponse)
async def get_top_projects(
    limit: int = Query(3, ge=1, le=10, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取排名靠前的项目（按Stars排序）"""
    items, total = search_projects_data(
        db,
        keyword=None,
        stars_min=None,
        stars_max=None,
        limit=limit,
        offset=0
    )
    
    project_items = [ProjectInfo(**item) for item in items]
    
    return ProjectSearchResponse(
        total=total,
        items=project_items
    )
