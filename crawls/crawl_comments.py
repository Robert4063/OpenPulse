import os
import json
import time
import sys
import re
from datetime import datetime, timezone
from dateutil import parser
from github import Github, GithubException, Auth, RateLimitExceededException
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()

TOKENS = os.getenv("GITHUB_TOKENS", "").split(",")
if not TOKENS or TOKENS == [""]:
    print("警告: 未设置 GITHUB_TOKENS 环境变量！")
    print("请创建 .env 文件并设置: GITHUB_TOKENS=your_token1,your_token2")
    sys.exit(1)
PROJECT_LIST_FILE = "top300_projects_list.txt"
DATA_DIR = "data"
COMMENT_DIR = os.path.join(DATA_DIR, "comment")
NUMBER_DIR = os.path.join(DATA_DIR, "comment_number") 
START_DATE = datetime(2022, 3, 1, tzinfo=timezone.utc)
END_DATE = datetime(2023, 3, 31, 23, 59, 59, tzinfo=timezone.utc)

def get_github_client(token_index):
    token = TOKENS[token_index % len(TOKENS)]
    auth = Auth.Token(token)
    return Github(auth=auth)

def ensure_dirs():
    if not os.path.exists(COMMENT_DIR):
        os.makedirs(COMMENT_DIR)
    if not os.path.exists(NUMBER_DIR):
        os.makedirs(NUMBER_DIR)

def get_projects():
    projects = []
    if os.path.exists(PROJECT_LIST_FILE):
        with open(PROJECT_LIST_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if '→' in line:
                    projects.append(line.split('→')[1].strip())
                else:
                    projects.append(line)
    return projects

def get_checkpoint_path(repo_name):
    safe_name = repo_name.replace('/', '_')
    return os.path.join(NUMBER_DIR, f"{safe_name}.txt")

def read_checkpoint(repo_name):
    path = get_checkpoint_path(repo_name)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.isdigit():
                    return int(content)
        except:
            return 0
    return 0

def write_checkpoint(repo_name, count):
    path = get_checkpoint_path(repo_name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(count))

def append_data(repo_name, data_list):
    if not data_list:
        return

    safe_name = repo_name.replace('/', '_')
    file_path = os.path.join(COMMENT_DIR, f"{safe_name}.json")
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, 'rb+') as f:
                f.seek(0, os.SEEK_END)
                pos = f.tell() - 1
                found = False
                while pos >= 0:
                    f.seek(pos)
                    char = f.read(1)
                    if char == b']':
                        found = True
                        break
                    pos -= 1
                
                if found:
                    f.seek(pos)
                    needs_comma = True
                    scan_pos = pos - 1
                    while scan_pos >= 0:
                        f.seek(scan_pos)
                        c = f.read(1)
                        if c in (b' ', b'\n', b'\r', b'\t'):
                            scan_pos -= 1
                            continue
                        if c == b'[':
                            needs_comma = False
                        break

                    f.seek(pos)
                    
                    json_str = json.dumps(data_list, ensure_ascii=False, indent=2)
                    inner = json_str.strip()
                    if inner.startswith('['): inner = inner[1:]
                    if inner.endswith(']'): inner = inner[:-1]
                    
                    inner_bytes = inner.encode('utf-8')
                    
                    if needs_comma:
                        f.write(b',' + inner_bytes + b']')
                    else:
                        f.write(inner_bytes + b']')
                    f.truncate()
        except Exception as e:
            print(f"Error appending to JSON: {e}")
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=2)

def serialize_comment(comment):
    c_created = comment.created_at
    if c_created.tzinfo is None:
        c_created = c_created.replace(tzinfo=timezone.utc)
    
    c_updated = comment.updated_at
    if c_updated and c_updated.tzinfo is None:
        c_updated = c_updated.replace(tzinfo=timezone.utc)

    return {
        "id": comment.id,
        "body": comment.body,
        "user": comment.user.login if comment.user else None,
        "created_time": c_created.isoformat(),
        "updated_time": c_updated.isoformat() if c_updated else None,
        "html_url": comment.html_url,
        "issue_url": comment.issue_url
    }

def process_repo(g, repo_name):
    print(f"[{repo_name}] Starting...")
    
    try:
        repo = g.get_repo(repo_name)
    except Exception as e:
        print(f"[{repo_name}] Error accessing repo: {e}")
        return

    processed_issues_count = read_checkpoint(repo_name)
    print(f"[{repo_name}] Resuming from Issue count: {processed_issues_count}")

    try:
        issues = repo.get_issues(state='all', sort='updated', direction='asc', since=START_DATE)
        
        buffer = []
        pbar = tqdm(desc=f"[{repo_name}]", unit=" issues", initial=processed_issues_count)
        
        current_count = 0
        
        for issue in issues:
            if current_count < processed_issues_count:
                current_count += 1
                continue
            
            try:
                comments = issue.get_comments()
                
                valid_comments = []
                for comment in comments:
                    c_created = comment.created_at
                    if c_created.tzinfo is None:
                        c_created = c_created.replace(tzinfo=timezone.utc)
                    
                    if START_DATE <= c_created <= END_DATE:
                        valid_comments.append(serialize_comment(comment))
                
                if valid_comments:
                    issue_data = {
                        "issue_url": issue.html_url, # Using html_url as the main identifier link
                        "issue_api_url": issue.url,
                        "comments": valid_comments
                    }
                    buffer.append(issue_data)
                
                current_count += 1
                pbar.update(1)
                
                if len(buffer) >= 20:
                    append_data(repo_name, buffer)
                    write_checkpoint(repo_name, current_count)
                    buffer = []

            except RateLimitExceededException:
                raise 
            except Exception as e:
                print(f"Error processing issue {issue.number}: {e}")
                current_count += 1
                continue

        if buffer:
            append_data(repo_name, buffer)
            write_checkpoint(repo_name, current_count)
        
        pbar.close()
        print(f"[{repo_name}] Done. Total issues scanned: {current_count}")

    except RateLimitExceededException:
        print(f"[{repo_name}] Rate limit exceeded.")
        raise
    except Exception as e:
        print(f"[{repo_name}] Error: {e}")


def main():
    ensure_dirs()
    
    if len(sys.argv) > 1:
        projects = [sys.argv[1]]
    else:
        projects = get_projects()
        
    print(f"Found {len(projects)} projects.")
    
    token_index = 0
    g = get_github_client(token_index)
    
    for repo_name in projects:
        while True:
            try:
                process_repo(g, repo_name)
                break
            except RateLimitExceededException:
                print(f"Rate limit reached for token {token_index % len(TOKENS)}. Switching token...")
                token_index += 1
                g = get_github_client(token_index)
                
                if token_index % len(TOKENS) == 0:
                    print("All tokens exhausted. Sleeping for 60 seconds...")
                    time.sleep(60)
                continue
            except Exception as e:
                print(f"Critical error processing {repo_name}: {e}")
                break

if __name__ == "__main__":
    main()
