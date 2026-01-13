"""
Comment 数据服务
从 JSON 文件读取评论数据并进行分析
"""
import os
import json
from typing import Dict, List, Optional
from collections import defaultdict
from functools import lru_cache

# 评论数据目录
COMMENT_CLEANED_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data", "comment_cleaned"
)


def get_username(user_field) -> Optional[str]:
    """
    从 user 字段提取用户名
    user 可能是字符串或包含 login 字段的字典
    """
    if user_field is None:
        return None
    if isinstance(user_field, str):
        return user_field
    if isinstance(user_field, dict):
        return user_field.get("login")
    return None


def get_project_from_issue_url(issue_url: str) -> Optional[str]:
    """
    从 issue_url 提取项目名
    例如: https://api.github.com/repos/AUTOMATIC1111/stable-diffusion-webui/issues/1
    -> AUTOMATIC1111_stable-diffusion-webui
    """
    try:
        # 处理 api.github.com 格式
        if "api.github.com/repos/" in issue_url:
            parts = issue_url.split("api.github.com/repos/")[1].split("/issues/")[0]
            return parts.replace("/", "_")
        # 处理 github.com 格式
        if "github.com/" in issue_url:
            parts = issue_url.split("github.com/")[1].split("/issues/")[0]
            return parts.replace("/", "_")
    except:
        pass
    return None


class CommentService:
    """评论数据服务"""
    
    def __init__(self):
        self.comment_dir = COMMENT_CLEANED_DIR
    
    def _get_comment_files(self) -> List[str]:
        """获取所有评论 JSON 文件"""
        if not os.path.exists(self.comment_dir):
            return []
        return [f for f in os.listdir(self.comment_dir) if f.endswith('.json')]
    
    def _normalize_to_filename(self, project: str) -> str:
        """将项目名标准化为文件名格式 (owner_repo)"""
        if '/' in project:
            return project.replace('/', '_')
        return project
    
    def get_contributors_for_project(
        self, 
        project_key: str, 
        top_n: int = 10
    ) -> Dict:
        """
        获取指定项目的贡献者统计（优化：直接读取对应的项目文件）
        
        Args:
            project_key: 项目标识 (如 facebook/react 或 facebook_react)
            top_n: 返回 Top N 贡献者
            
        Returns:
            {
                "total_contributors": int,
                "total_comments": int,
                "contributors": [
                    {"username": str, "comment_count": int, "percentage": float}
                ]
            }
        """
        contributor_counts = defaultdict(int)
        total_comments = 0
        
        # 直接读取对应项目的文件（优化：不再遍历所有文件）
        filename = self._normalize_to_filename(project_key) + ".json"
        filepath = os.path.join(self.comment_dir, filename)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                
                # 处理数据 - 支持两种格式
                if isinstance(data, dict):
                    # 新格式: {"issues": [{"comments": [...]}]}
                    if "issues" in data:
                        for issue in data.get("issues", []):
                            for comment in issue.get("comments", []):
                                username = get_username(comment.get("user"))
                                if username:
                                    contributor_counts[username] += 1
                                    total_comments += 1
                    # 旧格式: {"comments": [...]}
                    elif "comments" in data:
                        for comment in data.get("comments", []):
                            username = get_username(comment.get("user"))
                            if username:
                                contributor_counts[username] += 1
                                total_comments += 1
                # 数组格式
                elif isinstance(data, list):
                    for item in data:
                        for comment in item.get("comments", []):
                            username = get_username(comment.get("user"))
                            if username:
                                contributor_counts[username] += 1
                                total_comments += 1
                            
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        
        # 排序并取 Top N
        sorted_contributors = sorted(
            contributor_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        contributors = []
        for username, count in sorted_contributors:
            percentage = round(count / total_comments * 100, 2) if total_comments > 0 else 0
            contributors.append({
                "username": username,
                "comment_count": count,
                "percentage": percentage
            })
        
        return {
            "total_contributors": len(contributor_counts),
            "total_comments": total_comments,
            "contributors": contributors
        }
    
    def get_all_contributors_summary(self, top_n: int = 20) -> Dict:
        """
        获取所有项目的贡献者汇总统计
        
        Returns:
            {
                "total_contributors": int,
                "total_comments": int,
                "top_contributors": [
                    {"username": str, "comment_count": int}
                ]
            }
        """
        contributor_counts = defaultdict(int)
        total_comments = 0
        
        for filename in self._get_comment_files():
            filepath = os.path.join(self.comment_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                
                items = [data] if isinstance(data, dict) else data
                
                for item in items:
                    for comment in item.get("comments", []):
                        username = get_username(comment.get("user"))
                        if username:
                            contributor_counts[username] += 1
                            total_comments += 1
                            
            except Exception as e:
                continue
        
        sorted_contributors = sorted(
            contributor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        return {
            "total_contributors": len(contributor_counts),
            "total_comments": total_comments,
            "top_contributors": [
                {"username": u, "comment_count": c}
                for u, c in sorted_contributors
            ]
        }


# 单例
comment_service = CommentService()
