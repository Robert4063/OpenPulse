"""
数据模型（Pydantic schemas）
用于API请求和响应的数据结构定义
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ========== 搜索相关模型 ==========

class ProjectInfo(BaseModel):
    """项目信息"""
    id: Optional[int] = None
    repo_name: str
    project_key: Optional[str] = None
    stars: int = 0
    forks: int = 0
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProjectSearchResponse(BaseModel):
    """项目搜索响应"""
    total: int
    items: List[ProjectInfo]

# ========== 统计相关模型 ==========

class TrendData(BaseModel):
    """趋势数据 - 包含每日新增和累计总量"""
    labels: List[str]           # 日期标签
    values: List[int]           # 每日新增
    totals: Optional[List[int]] = None  # 累计总量（可选）

class ProjectSummary(BaseModel):
    """项目摘要"""
    project: str
    repo_name: str
    total_stars: int = 0
    total_forks: int = 0

class ProjectTrends(BaseModel):
    """项目所有趋势数据 - Stars 和 Forks"""
    summary: ProjectSummary
    stars_trend: TrendData
    forks_trend: TrendData


# ========== 贡献者相关模型 ==========

class ContributorInfo(BaseModel):
    """贡献者信息"""
    username: str
    commit_count: int = 0        # commit 数量
    comment_count: int = 0       # 评论数量（兼容旧字段）
    percentage: float = 0.0      # 占比
    github_url: Optional[str] = None  # GitHub 个人主页链接

class ContributorsResponse(BaseModel):
    """活跃贡献者统计响应"""
    total_contributors: int
    total_commits: int = 0
    total_comments: int = 0      # 兼容旧字段
    contributors: List[ContributorInfo]
    
    # 用于饼图的数据
    @property
    def chart_data(self) -> dict:
        """生成饼图数据"""
        labels = [c.username for c in self.contributors]
        values = [c.commit_count for c in self.contributors]
        return {"labels": labels, "values": values}

class ContributorChartData(BaseModel):
    """贡献者饼图数据"""
    labels: List[str]
    values: List[int]


# ========== 健康度评估相关模型 ==========

class HealthDimensionDetails(BaseModel):
    """健康度维度详情"""
    class Config:
        extra = "allow"  # 允许额外字段

class HealthDimension(BaseModel):
    """健康度单个维度"""
    name: str
    weight: str
    score: float
    details: dict = {}
    
    class Config:
        extra = "allow"

class HealthDimensions(BaseModel):
    """健康度所有维度"""
    growth: HealthDimension
    activity: HealthDimension
    contribution: HealthDimension
    code: HealthDimension

class HealthWeights(BaseModel):
    """健康度权重配置"""
    growth: float
    activity: float
    contribution: float
    code: float

class HealthScoreResponse(BaseModel):
    """健康度评分完整响应"""
    project: str
    repo_name: str
    final_score: float
    grade: str
    grade_label: str
    grade_color: str
    weights: HealthWeights
    dimensions: HealthDimensions
    calculated_at: str

class HealthScoreSummary(BaseModel):
    """健康度评分摘要（简化版）"""
    project: str
    repo_name: str
    final_score: float
    grade: str
    grade_label: str
    grade_color: str
    growth_score: float
    activity_score: float
    contribution_score: float
    code_score: float
