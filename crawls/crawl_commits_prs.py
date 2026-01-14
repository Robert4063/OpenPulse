"""
Commit Activity 和 PR 数量爬虫脚本
使用GitHub API爬取top300项目每天的commit数量和PR数量

功能:
- 断点续传支持
- 多Token轮换
- 获取每个项目的每日commit数量
- 获取每个项目的每日PR创建数量
- 数据存储到 data/commit_activity/ 和 data/pr_daily/ 目录

参考: crawls/crawl_stars.py 的存储路径结构
"""

import os
import json
import time
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import requests
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

TOKENS = [
    os.getenv("GITHUB_TOKEN_1", "your_github_token_1"),
    os.getenv("GITHUB_TOKEN_2", "your_github_token_2"),
    os.getenv("GITHUB_TOKEN_3", "your_github_token_3"),
    os.getenv("GITHUB_TOKEN_4", "your_github_token_4"),
]
PROJECT_LIST_FILE = "top300_projects_list.txt"
DATA_DIR = "data"
COMMIT_DIR = os.path.join(DATA_DIR, "commit_activity")
PR_DIR = os.path.join(DATA_DIR, "pr_daily")
CHECKPOINT_DIR = os.path.join(DATA_DIR, "commits_prs_checkpoint")

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
            'Accept': 'application/vnd.github.v3+json',
            'X-GitHub-Api-Version': '2022-11-28'
        })
    
    def switch_token(self):
        self.current_token_index += 1
        self._update_headers()
        print(f"切换到Token {self.current_token_index % len(self.tokens) + 1}")
        return self.current_token_index
    
    def get_rate_limit_info(self):
        url = "https://api.github.com/rate_limit"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                core = data.get('resources', {}).get('core', {})
                search = data.get('resources', {}).get('search', {})
                return {
                    'core_remaining': core.get('remaining', 0),
                    'core_reset': core.get('reset', 0),
                    'search_remaining': search.get('remaining', 0),
                    'search_reset': search.get('reset', 0)
                }
        except:
            pass
        return {'core_remaining': 0, 'core_reset': 0, 'search_remaining': 0, 'search_reset': 0}
    
    def get_with_retry(self, url, params=None, max_retries=3, is_search=False):
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                
                remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
                if remaining == 0:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = max(reset_time - time.time(), 0) + 5
                    print(f"\nRate limit达到，切换token...")
                    old_index = self.current_token_index
                    self.switch_token()
                    if self.current_token_index >= old_index + len(self.tokens):
                        actual_wait = min(wait_time, 60) if is_search else min(wait_time, 30)
                        print(f"所有token都达到限制，等待 {actual_wait:.0f} 秒...")
                        time.sleep(actual_wait)
                    continue
                
                if response.status_code == 200:
                    return response.json(), response.headers
                elif response.status_code == 202:
                    print(f"\n数据生成中，等待2秒后重试...")
                    time.sleep(2)
                    continue
                elif response.status_code == 403:
                    error_msg = response.json().get('message', '')
                    if 'rate limit' in error_msg.lower() or 'secondary rate limit' in error_msg.lower():
                        print(f"\n403 Rate limit, 切换token...")
                        self.switch_token()
                        time.sleep(2)
                        continue
                    else:
                        print(f"\n403 Forbidden: {error_msg}")
                        return None, None
                elif response.status_code == 404:
                    return None, None
                elif response.status_code == 422:
                    print(f"\n422 Unprocessable: {response.text[:200]}")
                    return None, None
                elif response.status_code == 409:
                    print(f"\n409 Conflict (可能是空仓库)")
                    return None, None
                else:
                    print(f"\nHTTP {response.status_code}: {response.text[:200]}")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                print(f"\n请求错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                time.sleep(5)
        
        return None, None

    def get_commits_page(self, owner, repo, since=None, until=None, page=1, per_page=100):
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        params = {'page': page, 'per_page': per_page}
        if since:
            params['since'] = since.isoformat()
        if until:
            params['until'] = until.isoformat()
        data, headers = self.get_with_retry(url, params)
        return data, headers
    
    def get_prs_page(self, owner, repo, state='all', page=1, per_page=100):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {
            'state': state,
            'sort': 'created',
            'direction': 'desc',
            'page': page, 
            'per_page': per_page
        }
        data, headers = self.get_with_retry(url, params)
        return data, headers
    
    def search_prs(self, repo, created_date):
        url = "https://api.github.com/search/issues"
        query = f"repo:{repo} is:pr created:{created_date}"
        params = {'q': query, 'per_page': 1}
        data, headers = self.get_with_retry(url, params, is_search=True)
        if data:
            return data.get('total_count', 0)
        return 0


def ensure_dirs():
    for d in [COMMIT_DIR, PR_DIR, CHECKPOINT_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)


def get_projects():
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
    return repo_name.replace('/', '_')


def get_checkpoint_path(repo_name, data_type):
    safe_name = get_safe_name(repo_name)
    return os.path.join(CHECKPOINT_DIR, f"{safe_name}_{data_type}.json")


def get_output_path(repo_name, data_type):
    safe_name = get_safe_name(repo_name)
    if data_type == 'commits':
        return os.path.join(COMMIT_DIR, f"{safe_name}_commits.json")
    else:
        return os.path.join(PR_DIR, f"{safe_name}_prs.json")


def read_checkpoint(repo_name, data_type):
    path = get_checkpoint_path(repo_name, data_type)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"last_page": 0, "daily_counts": {}, "completed": False}


def write_checkpoint(repo_name, data_type, checkpoint_data):
    path = get_checkpoint_path(repo_name, data_type)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)


def save_result(repo_name, data_type, daily_counts, total_count):
    path = get_output_path(repo_name, data_type)
    
    sorted_dates = sorted(daily_counts.keys())
    
    result = {
        "project": repo_name,
        "data_type": data_type,
        f"total_{data_type}_in_range": sum(daily_counts.values()),
        f"total_{data_type}_all_time": total_count,
        "start_date": START_DATE.strftime("%Y-%m-%d"),
        "end_date": END_DATE.strftime("%Y-%m-%d"),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        f"daily_{data_type}": {date: daily_counts[date] for date in sorted_dates}
    }
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def process_commits(crawler, repo_name):
    parts = repo_name.split('/')
    if len(parts) != 2:
        print(f"⚠️  跳过无效项目格式: {repo_name}")
        return False
    
    owner, repo = parts
    
    checkpoint = read_checkpoint(repo_name, 'commits')
    
    if checkpoint.get("completed", False):
        print(f"  [Commits] 已完成，跳过")
        return True
    
    last_page = checkpoint.get("last_page", 0)
    daily_commits = defaultdict(int, checkpoint.get("daily_counts", {}))
    
    print(f"  [Commits] 开始爬取，从第 {last_page + 1} 页继续...")
    
    page = last_page + 1
    total_commits = 0
    commits_in_range = 0
    
    pbar = tqdm(desc=f"    Commits", unit=" pages", initial=last_page, leave=False)
    
    try:
        while True:
            data, headers = crawler.get_commits_page(
                owner, repo, 
                since=START_DATE, 
                until=END_DATE,
                page=page, 
                per_page=100
            )
            
            if data is None or len(data) == 0:
                break
            
            for commit_info in data:
                total_commits += 1
                
                commit_data = commit_info.get('commit', {})
                committer = commit_data.get('committer', {})
                commit_date_str = committer.get('date')
                
                if not commit_date_str:
                    author = commit_data.get('author', {})
                    commit_date_str = author.get('date')
                
                if not commit_date_str:
                    continue
                
                try:
                    commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))
                except:
                    continue
                
                if START_DATE <= commit_date <= END_DATE:
                    date_str = commit_date.strftime("%Y-%m-%d")
                    daily_commits[date_str] += 1
                    commits_in_range += 1
            
            pbar.update(1)
            
            link_header = headers.get('Link', '') if headers else ''
            if 'rel="next"' not in link_header:
                break
            
            if page % 10 == 0:
                checkpoint_data = {
                    "last_page": page,
                    "daily_counts": dict(daily_commits),
                    "completed": False
                }
                write_checkpoint(repo_name, 'commits', checkpoint_data)
            
            page += 1
            
            time.sleep(0.1)
        
        pbar.close()
        
        save_result(repo_name, 'commits', dict(daily_commits), total_commits)
        
        checkpoint_data = {
            "last_page": page,
            "daily_counts": dict(daily_commits),
            "completed": True
        }
        write_checkpoint(repo_name, 'commits', checkpoint_data)
        
        print(f"  [Commits] 完成! 总数: {total_commits}, 范围内: {commits_in_range}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n  [Commits] 用户中断，保存进度...")
        checkpoint_data = {
            "last_page": page - 1,
            "daily_counts": dict(daily_commits),
            "completed": False
        }
        write_checkpoint(repo_name, 'commits', checkpoint_data)
        raise
    except Exception as e:
        print(f"\n  [Commits] 错误: {e}")
        import traceback
        traceback.print_exc()
        checkpoint_data = {
            "last_page": page - 1,
            "daily_counts": dict(daily_commits),
            "completed": False
        }
        write_checkpoint(repo_name, 'commits', checkpoint_data)
        return False


def process_prs(crawler, repo_name):
    parts = repo_name.split('/')
    if len(parts) != 2:
        print(f"⚠️  跳过无效项目格式: {repo_name}")
        return False
    
    owner, repo = parts
    
    checkpoint = read_checkpoint(repo_name, 'prs')
    
    if checkpoint.get("completed", False):
        print(f"  [PRs] 已完成，跳过")
        return True
    
    last_page = checkpoint.get("last_page", 0)
    daily_prs = defaultdict(int, checkpoint.get("daily_counts", {}))
    
    print(f"  [PRs] 开始爬取，从第 {last_page + 1} 页继续...")
    
    page = last_page + 1
    total_prs = 0
    prs_in_range = 0
    passed_start_date = False 
    
    pbar = tqdm(desc=f"    PRs", unit=" pages", initial=last_page, leave=False)
    
    try:
        while True:
            data, headers = crawler.get_prs_page(owner, repo, state='all', page=page, per_page=100)
            
            if data is None or len(data) == 0:
                break
            
            for pr_info in data:
                total_prs += 1
                
                created_at_str = pr_info.get('created_at')
                if not created_at_str:
                    continue
                
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except:
                    continue
                
                if START_DATE <= created_at <= END_DATE:
                    date_str = created_at.strftime("%Y-%m-%d")
                    daily_prs[date_str] += 1
                    prs_in_range += 1
                
                if created_at < START_DATE:
                    passed_start_date = True
            
            pbar.update(1)
            
            if passed_start_date:
                all_before = all(
                    datetime.fromisoformat(pr.get('created_at', '').replace('Z', '+00:00')) < START_DATE
                    for pr in data if pr.get('created_at')
                )
                if all_before:
                    break
            
            link_header = headers.get('Link', '') if headers else ''
            if 'rel="next"' not in link_header:
                break
            
            if page % 10 == 0:
                checkpoint_data = {
                    "last_page": page,
                    "daily_counts": dict(daily_prs),
                    "completed": False
                }
                write_checkpoint(repo_name, 'prs', checkpoint_data)
            
            page += 1
            
            time.sleep(0.1)
        
        pbar.close()
        
        save_result(repo_name, 'prs', dict(daily_prs), total_prs)
        
        checkpoint_data = {
            "last_page": page,
            "daily_counts": dict(daily_prs),
            "completed": True
        }
        write_checkpoint(repo_name, 'prs', checkpoint_data)
        
        print(f"  [PRs] 完成! 总数: {total_prs}, 范围内: {prs_in_range}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n  [PRs] 用户中断，保存进度...")
        checkpoint_data = {
            "last_page": page - 1,
            "daily_counts": dict(daily_prs),
            "completed": False
        }
        write_checkpoint(repo_name, 'prs', checkpoint_data)
        raise
    except Exception as e:
        print(f"\n  [PRs] 错误: {e}")
        import traceback
        traceback.print_exc()
        checkpoint_data = {
            "last_page": page - 1,
            "daily_counts": dict(daily_prs),
            "completed": False
        }
        write_checkpoint(repo_name, 'prs', checkpoint_data)
        return False


def process_repo(crawler, repo_name):
    commit_success = process_commits(crawler, repo_name)
    pr_success = process_prs(crawler, repo_name)
    return commit_success and pr_success


def main():
    print("=" * 60)
    print("📊 GitHub Commit Activity & PR 数据爬虫 (每日统计)")
    print("=" * 60)
    print(f"\n📁 项目列表: {PROJECT_LIST_FILE}")
    print(f"📁 Commit数据目录: {COMMIT_DIR}")
    print(f"📁 PR数据目录: {PR_DIR}")
    print(f"📁 断点目录: {CHECKPOINT_DIR}")
    print(f"🔑 Token数量: {len(TOKENS)}")
    print(f"📅 时间范围: {START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
    
    ensure_dirs()
    
    if len(sys.argv) > 1:
        projects = [sys.argv[1]]
    else:
        projects = get_projects()
    
    if not projects:
        print("❌ 未找到项目列表")
        return
    
    print(f"\n📋 找到 {len(projects)} 个项目")
    
    crawler = GitHubCrawler(TOKENS)
    
    rate_info = crawler.get_rate_limit_info()
    print(f"📊 当前Token剩余请求次数: Core={rate_info['core_remaining']}, Search={rate_info['search_remaining']}")
    
    print(f"\n🚀 开始爬取...\n")
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, repo_name in enumerate(projects):
        print(f"\n[{i+1}/{len(projects)}] 处理: {repo_name}")
        
        commit_checkpoint = read_checkpoint(repo_name, 'commits')
        pr_checkpoint = read_checkpoint(repo_name, 'prs')
        if commit_checkpoint.get("completed", False) and pr_checkpoint.get("completed", False):
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
            crawler.switch_token()
    
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
