"""
Star数据爬虫脚本
使用GitHub API爬取top300项目每天的star数量

功能:
- 断点续传支持
- 多Token轮换
- 获取每个项目的stargazers及其star时间
- 按日期统计每天的star数量
- 数据存储到 data/star/ 目录

参考: crawls/crawl_comments.py 的存储路径结构
"""

import os
import json
import time
import sys
from datetime import datetime, timezone
from collections import defaultdict
import requests
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
TOKENS = [
    os.getenv("GITHUB_TOKEN_1", "your_github_token_1"),
    os.getenv("GITHUB_TOKEN_2", "your_github_token_2"),
    os.getenv("GITHUB_TOKEN_3", "your_github_token_3"),
    os.getenv("GITHUB_TOKEN_4", "your_github_token_4"),
]
PROJECT_LIST_FILE = "top300_projects_list.txt"
DATA_DIR = "data"
STAR_DIR = os.path.join(DATA_DIR, "star")
CHECKPOINT_DIR = os.path.join(DATA_DIR, "star_checkpoint")

# 时间范围设置（可按需调整）
START_DATE = datetime(2022, 3, 1, tzinfo=timezone.utc)
END_DATE = datetime(2023, 3, 31, 23, 59, 59, tzinfo=timezone.utc)


class GitHubCrawler:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.session = requests.Session()
        self._update_headers()
    
    def _update_headers(self):
        token = self.tokens[self.current_token_index % len(self.tokens)]
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            # 使用特殊的Accept头来获取star时间戳
            'Accept': 'application/vnd.github.star+json',
            'X-GitHub-Api-Version': '2022-11-28'
        })
    
    def switch_token(self):
        self.current_token_index += 1
        self._update_headers()
        print(f"切换到Token {self.current_token_index % len(self.tokens) + 1}")
        return self.current_token_index
    
    def get_rate_limit_info(self):
        """获取当前token的rate limit信息"""
        url = "https://api.github.com/rate_limit"
        try:
            # 临时使用标准Accept头
            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                core = data.get('resources', {}).get('core', {})
                return core.get('remaining', 0), core.get('reset', 0)
        except:
            pass
        return 0, 0
    
    def get_with_retry(self, url, params=None, max_retries=3):
        """带重试和token切换的GET请求"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                # 检查rate limit
                remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
                if remaining == 0:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = max(reset_time - time.time(), 0) + 5
                    print(f"\nRate limit达到，切换token...")
                    old_index = self.current_token_index
                    self.switch_token()
                    # 如果已经轮换了一轮所有token，等待
                    if self.current_token_index >= old_index + len(self.tokens):
                        print(f"所有token都达到限制，等待 {min(wait_time, 60):.0f} 秒...")
                        time.sleep(min(wait_time, 60))
                    continue
                
                if response.status_code == 200:
                    return response.json(), response.headers
                elif response.status_code == 403:
                    error_msg = response.json().get('message', '')
                    if 'rate limit' in error_msg.lower():
                        print(f"\n403 Rate limit, 切换token...")
                        self.switch_token()
                        continue
                    else:
                        print(f"\n403 Forbidden: {error_msg}")
                        return None, None
                elif response.status_code == 404:
                    return None, None
                elif response.status_code == 422:
                    # 通常是分页超过限制
                    return None, None
                else:
                    print(f"\nHTTP {response.status_code}: {response.text[:200]}")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                print(f"\n请求错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                time.sleep(5)
        
        return None, None

    def get_stargazers_page(self, owner, repo, page=1, per_page=100):
        """获取一页stargazers（带时间戳）"""
        url = f"https://api.github.com/repos/{owner}/{repo}/stargazers"
        params = {'page': page, 'per_page': per_page}
        data, headers = self.get_with_retry(url, params)
        return data, headers


def ensure_dirs():
    """确保目录存在"""
    if not os.path.exists(STAR_DIR):
        os.makedirs(STAR_DIR)
    if not os.path.exists(CHECKPOINT_DIR):
        os.makedirs(CHECKPOINT_DIR)


def get_projects():
    """读取项目列表"""
    projects = []
    if not os.path.exists(PROJECT_LIST_FILE):
        print(f"Error: {PROJECT_LIST_FILE} not found.")
        return []
        
    with open(PROJECT_LIST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            if '→' in line:
                projects.append(line.split('→')[-1].strip())
            else:
                projects.append(line)
    return projects


def get_safe_name(repo_name):
    """将 owner/repo 转换为安全的文件名"""
    return repo_name.replace('/', '_')


def get_checkpoint_path(repo_name):
    """获取断点文件路径"""
    safe_name = get_safe_name(repo_name)
    return os.path.join(CHECKPOINT_DIR, f"{safe_name}.json")


def get_output_path(repo_name):
    """获取输出文件路径"""
    safe_name = get_safe_name(repo_name)
    return os.path.join(STAR_DIR, f"{safe_name}.json")


def read_checkpoint(repo_name):
    """读取断点信息"""
    path = get_checkpoint_path(repo_name)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"last_page": 0, "daily_stars": {}, "completed": False}


def write_checkpoint(repo_name, checkpoint_data):
    """写入断点信息"""
    path = get_checkpoint_path(repo_name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)


def save_result(repo_name, daily_stars, total_stars):
    """保存最终结果"""
    path = get_output_path(repo_name)
    
    # 将日期字符串排序
    sorted_dates = sorted(daily_stars.keys())
    
    result = {
        "project": repo_name,
        "total_stars_in_range": sum(daily_stars.values()),
        "total_stars_all_time": total_stars,
        "start_date": START_DATE.strftime("%Y-%m-%d"),
        "end_date": END_DATE.strftime("%Y-%m-%d"),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "daily_stars": {date: daily_stars[date] for date in sorted_dates}
    }
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def process_repo(crawler, repo_name):
    """处理单个仓库"""
    parts = repo_name.split('/')
    if len(parts) != 2:
        print(f"⚠️  跳过无效项目格式: {repo_name}")
        return False
    
    owner, repo = parts
    
    # 读取断点
    checkpoint = read_checkpoint(repo_name)
    
    if checkpoint.get("completed", False):
        print(f"[{repo_name}] 已完成，跳过")
        return True
    
    last_page = checkpoint.get("last_page", 0)
    daily_stars = defaultdict(int, checkpoint.get("daily_stars", {}))
    
    print(f"[{repo_name}] 开始爬取，从第 {last_page + 1} 页继续...")
    
    page = last_page + 1
    total_stars = 0
    stars_in_range = 0
    
    # 使用while循环分页获取所有stargazers
    pbar = tqdm(desc=f"[{repo_name}]", unit=" pages", initial=last_page)
    
    try:
        while True:
            data, headers = crawler.get_stargazers_page(owner, repo, page=page, per_page=100)
            
            if data is None or len(data) == 0:
                break
            
            for star_info in data:
                total_stars += 1
                
                # 解析star时间
                starred_at_str = star_info.get('starred_at')
                if not starred_at_str:
                    continue
                
                try:
                    starred_at = datetime.fromisoformat(starred_at_str.replace('Z', '+00:00'))
                except:
                    continue
                
                # 检查是否在时间范围内
                if START_DATE <= starred_at <= END_DATE:
                    date_str = starred_at.strftime("%Y-%m-%d")
                    daily_stars[date_str] += 1
                    stars_in_range += 1
            
            pbar.update(1)
            
            # 检查是否还有下一页
            link_header = headers.get('Link', '') if headers else ''
            if 'rel="next"' not in link_header:
                break
            
            # 每10页保存一次断点
            if page % 10 == 0:
                checkpoint_data = {
                    "last_page": page,
                    "daily_stars": dict(daily_stars),
                    "completed": False
                }
                write_checkpoint(repo_name, checkpoint_data)
            
            page += 1
            
            # 避免请求过快
            time.sleep(0.1)
        
        pbar.close()
        
        # 保存最终结果
        save_result(repo_name, dict(daily_stars), total_stars)
        
        # 标记为完成
        checkpoint_data = {
            "last_page": page,
            "daily_stars": dict(daily_stars),
            "completed": True
        }
        write_checkpoint(repo_name, checkpoint_data)
        
        print(f"[{repo_name}] 完成! 总star: {total_stars}, 范围内: {stars_in_range}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n[{repo_name}] 用户中断，保存进度...")
        checkpoint_data = {
            "last_page": page - 1,
            "daily_stars": dict(daily_stars),
            "completed": False
        }
        write_checkpoint(repo_name, checkpoint_data)
        raise
    except Exception as e:
        print(f"\n[{repo_name}] 错误: {e}")
        # 保存当前进度
        checkpoint_data = {
            "last_page": page - 1,
            "daily_stars": dict(daily_stars),
            "completed": False
        }
        write_checkpoint(repo_name, checkpoint_data)
        return False


def main():
    print("=" * 60)
    print("⭐ GitHub Star数据爬虫 (每日统计)")
    print("=" * 60)
    print(f"\n📁 项目列表: {PROJECT_LIST_FILE}")
    print(f"📁 数据目录: {STAR_DIR}")
    print(f"📁 断点目录: {CHECKPOINT_DIR}")
    print(f"🔑 Token数量: {len(TOKENS)}")
    print(f"📅 时间范围: {START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
    
    # 确保目录存在
    ensure_dirs()
    
    # 读取项目列表
    if len(sys.argv) > 1:
        projects = [sys.argv[1]]
    else:
        projects = get_projects()
    
    if not projects:
        print("❌ 未找到项目列表")
        return
    
    print(f"\n📋 找到 {len(projects)} 个项目")
    
    # 初始化爬虫
    crawler = GitHubCrawler(TOKENS)
    
    # 检查初始rate limit
    remaining, reset = crawler.get_rate_limit_info()
    print(f"📊 当前Token剩余请求次数: {remaining}")
    
    print(f"\n🚀 开始爬取...\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, repo_name in enumerate(projects):
        print(f"\n[{i+1}/{len(projects)}] 处理: {repo_name}")
        
        # 检查是否已完成
        checkpoint = read_checkpoint(repo_name)
        if checkpoint.get("completed", False):
            print(f"  ✓ 已完成，跳过")
            skipped_count += 1
            continue
        
        try:
            success = process_repo(crawler, repo_name)
            if success:
                success_count += 1
            else:
                error_count += 1
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断!")
            break
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            error_count += 1
            # 切换token尝试
            crawler.switch_token()
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 爬取统计")
    print("=" * 60)
    print(f"总项目数: {len(projects)}")
    print(f"成功: {success_count}")
    print(f"跳过(已完成): {skipped_count}")
    print(f"失败: {error_count}")
    print("\n✅ 爬取完成!")


if __name__ == "__main__":
    main()
