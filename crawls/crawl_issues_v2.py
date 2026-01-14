import os
import json
import sys
import time
import re
from datetime import datetime, timezone, timedelta
from github import Github, GithubException, Auth
from tqdm import tqdm
from dateutil import parser

TOKENS = [
    os.getenv("GITHUB_TOKEN_1", "your_github_token_1"),
    os.getenv("GITHUB_TOKEN_2", "your_github_token_2"),
    os.getenv("GITHUB_TOKEN_3", "your_github_token_3"),
    os.getenv("GITHUB_TOKEN_4", "your_github_token_4"),
]
PROJECT_LIST_FILE = "top300_projects_list.txt"

def get_github_client(token_index):
    token = TOKENS[token_index % len(TOKENS)]
    auth = Auth.Token(token)
    return Github(auth=auth)

OUTPUT_DIR = os.path.join("data", "issue")
NUMBER_DIR = os.path.join("data", "issue_numbers")

FIXED_START_DATE = datetime(2022, 3, 1, tzinfo=timezone.utc)
END_DATE = datetime(2023, 3, 31, 23, 59, 59, tzinfo=timezone.utc)

def ensure_dirs():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    if not os.path.exists(NUMBER_DIR):
        os.makedirs(NUMBER_DIR)

def get_projects():
    projects = []
    if not os.path.exists(PROJECT_LIST_FILE):
        print(f"Error: {PROJECT_LIST_FILE} not found.")
        return []
        
    with open(PROJECT_LIST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if '→' in line:
                projects.append(line.split('→')[-1].strip())
            else:
                projects.append(line)
    return projects

def read_checkpoint(filepath):
    """Read the number of crawled issues from file."""
    if not os.path.exists(filepath):
        return 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return 0
            
            lines = content.splitlines()
            
            # Legacy fallback: count lines if it looks like a list (more than 1 line)
            if len(lines) > 1:
                return len(lines)
            
            # New format: single count (1 line)
            if len(lines) == 1 and lines[0].isdigit():
                 return int(lines[0])
                 
            return 0
    except Exception as e:
        print(f"Error reading checkpoint {filepath}: {e}")
        return 0

def write_checkpoint(filepath, count):
    """Write the total count of crawled issues."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(count))
    except Exception as e:
        print(f"Error writing checkpoint {filepath}: {e}")

def append_issues_to_json(json_file, new_issues):
    """Append issues to a JSON file (handling array structure)."""
    if not new_issues:
        return
    
    if not os.path.exists(json_file):
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(new_issues, f, ensure_ascii=False, indent=2)
    else:
        try:
            with open(json_file, 'rb+') as f:
                f.seek(0, os.SEEK_END)
                filesize = f.tell()
                
                if filesize == 0:
                    f.write(json.dumps(new_issues, ensure_ascii=False, indent=2).encode('utf-8'))
                    return

                pos = filesize
                found_bracket = False
                while pos > 0:
                    pos -= 1
                    f.seek(pos)
                    char = f.read(1)
                    if char == b']':
                        found_bracket = True
                        break
                
                if not found_bracket:
                    return

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
                content = json.dumps(new_issues, ensure_ascii=False, indent=2)
                inner_content = content.strip()
                if inner_content.startswith('['): inner_content = inner_content[1:]
                if inner_content.endswith(']'): inner_content = inner_content[:-1]
                
                if needs_comma:
                    f.write(b',' + inner_content.encode('utf-8') + b']')
                else:
                    f.write(inner_content.encode('utf-8') + b']')
                f.truncate()
        except Exception as e:
            print(f"Error appending to JSON {json_file}: {e}")

def get_last_created_at(filepath):
    """
    Efficiently get the last 'created_at' date from a large JSON file.
    """
    try:
        with open(filepath, 'rb') as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            seek_size = min(5120, filesize)
            f.seek(-seek_size, os.SEEK_END)
            tail_data = f.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'"created_at":\s*"([^"]+)"', tail_data)
            if matches:
                dt = parser.parse(matches[-1])
                # Ensure timezone aware
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
    except Exception:
        return None
    return None

def serialize_issue(issue):
    return {
        "title": issue.title,
        "body": issue.body,
        "state": issue.state,
        "number": issue.number,
        "created_at": issue.created_at.isoformat() if issue.created_at else None,
        "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
        "labels": [label.name for label in issue.labels],
        "author_association": issue.author_association,
        "user": issue.user.login if issue.user else None,
        "html_url": issue.html_url
    }

def get_github_issue_count(g, project_name, start_date, end_date):
    try:
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        query_issues = f"repo:{project_name} created:{start_str}..{end_str} is:issue"
        query_prs = f"repo:{project_name} created:{start_str}..{end_str} is:pr"
        
        issues_count = g.search_issues(query_issues).totalCount
        time.sleep(1) 
        prs_count = g.search_issues(query_prs).totalCount
        
        return issues_count + prs_count
    except Exception as e:
        print(f"[{project_name}] Error getting total count: {e}")
        return None

def process_project(g, project_name):
    safe_name = project_name.replace('/', '_')
    json_file = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
    number_file = os.path.join(NUMBER_DIR, f"{safe_name}.txt")

    crawled_count = read_checkpoint(number_file)

    total_count = get_github_issue_count(g, project_name, FIXED_START_DATE, END_DATE)
    
    if total_count is not None:
        print(f"[{project_name}] Local count: {crawled_count}, GitHub total: {total_count}")
        if crawled_count >= total_count:
            print(f"[{project_name}] Already completed (Count match).")
            return "skipped"
    else:
        print(f"[{project_name}] Could not verify total count. Proceeding with crawl...")

    current_start_date = FIXED_START_DATE
    is_resuming = False
    
    if os.path.exists(json_file):
        last_date = get_last_created_at(json_file)
        if last_date and last_date > FIXED_START_DATE:
            current_start_date = last_date
            is_resuming = True
            print(f"[{project_name}] Resuming from {current_start_date}")
    
    if current_start_date >= END_DATE:
        print(f"[{project_name}] Date range exhausted.")
        return "skipped"

    try:
        repo = g.get_repo(project_name)
        
        issues = repo.get_issues(state='all', sort='created', direction='asc', since=current_start_date)
        
        new_batch = []
        current_count = crawled_count
        
        pbar_total = total_count if total_count else (crawled_count + 1000) # Estimate if None
        pbar = tqdm(desc=f"[{project_name}] Crawling", unit="issue", initial=crawled_count, total=pbar_total)
        
        for issue in issues:
            if issue.created_at < FIXED_START_DATE:
                continue
            
            if issue.created_at > END_DATE:
                break
            
            if is_resuming and issue.created_at <= current_start_date:
                continue

            data = serialize_issue(issue)
            new_batch.append(data)
            current_count += 1
            pbar.update(1)
            
            if len(new_batch) >= 50:
                append_issues_to_json(json_file, new_batch)
                write_checkpoint(number_file, current_count)
                new_batch = []
        
        if new_batch:
            append_issues_to_json(json_file, new_batch)
            write_checkpoint(number_file, current_count)
            
        pbar.close()
        print(f"[{project_name}] Done. Total issues: {current_count}")
        
    except GithubException as e:
        print(f"[{project_name}] GitHub Error: {e}")
        if e.status == 403 and 'rate limit' in str(e).lower():
            return "rate_limit"
    except Exception as e:
        print(f"[{project_name}] Error: {e}")
    
    return "ok"

def main():
    ensure_dirs()
    projects = get_projects()
    print(f"Found {len(projects)} projects.")
    
    token_index = 0
    g = get_github_client(token_index)
    
    for project in projects:
        while True:
            status = process_project(g, project)
            if status == "rate_limit":
                print(f"Rate limit reached for token {token_index % len(TOKENS)}. Switching token...")
                token_index += 1
                g = get_github_client(token_index)
                
                if token_index % len(TOKENS) == 0:
                    print("All tokens exhausted. Sleeping for 60 seconds...")
                    time.sleep(60)
                continue
            break 

if __name__ == "__main__":
    main()
