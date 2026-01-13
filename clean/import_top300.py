"""
将 top300_2022_2023.csv 文件导入到 Docker MySQL 容器 (openpulse_mysql) 的 github_data 数据库中

使用方法:
    python import_top300.py

可选参数:
    --mode replace|append|fail  导入模式（默认: replace）
    --chunksize N               每次读取的行数（默认: 50000）
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import BigInteger, Text, Integer
from sqlalchemy.dialects.mysql import LONGTEXT
import pymysql
import argparse
import os
import sys
import shutil
import subprocess
from datetime import datetime

# 禁用输出缓冲
sys.stdout.reconfigure(line_buffering=True)

# ====== 磁盘空间监控配置 ======
MIN_DISK_SPACE_GB = 10  # 最小剩余空间（GB）
DISK_TO_MONITOR = "C:\\"  # 监控的磁盘

def check_disk_space():
    """检查磁盘剩余空间，返回剩余空间（GB）"""
    total, used, free = shutil.disk_usage(DISK_TO_MONITOR)
    free_gb = free / (1024 ** 3)  # 转换为 GB
    return free_gb

def is_disk_space_low():
    """检查磁盘空间是否低于阈值"""
    free_gb = check_disk_space()
    return free_gb < MIN_DISK_SPACE_GB, free_gb

# ====== 1. 数据库配置 ======
DB_USER = 'root'
DB_PASSWORD = 'root'  # Docker MySQL 容器的 root 密码
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'openrankdata'  # 目标数据库名称

# ====== 2. CSV 文件配置 ======
CSV_FILE_PATH = r'D:\openrankdata\top300_20_23\top300_2022_2023.csv'
TARGET_TABLE = 'top300_2022_2023'  # 目标表名

def test_connection():
    """测试数据库连接并创建数据库（如果不存在）"""
    try:
        # 先尝试连接到 MySQL 服务器（不指定数据库）
        test_conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✅ MySQL 服务器连接成功！")
        
        # 检查数据库是否存在
        cursor = test_conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ 数据库 '{DB_NAME}' 已存在")
        else:
            print(f"⚠️  数据库 '{DB_NAME}' 不存在，正在创建...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 数据库 '{DB_NAME}' 创建成功")
        
        cursor.close()
        test_conn.close()
        return True
        
    except pymysql.err.OperationalError as e:
        if e.args[0] == 2003:
            print("❌ 无法连接到 MySQL 服务器！")
            print("\n可能的原因：")
            print("1. Docker MySQL 容器 (openpulse_mysql) 未启动")
            print("   - 检查容器状态: docker ps -a")
            print("   - 启动容器: docker start openpulse_mysql")
            print("2. MySQL 配置的端口不是 3306")
            print("3. 端口映射不正确，检查 Docker 端口映射")
            print(f"\n当前配置: {DB_HOST}:{DB_PORT}")
            print(f"数据库: {DB_NAME}, 用户: {DB_USER}")
        else:
            print(f"❌ 数据库连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return False

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='导入 top300_2022_2023.csv 到 MySQL 数据库')
    parser.add_argument('--mode', choices=['replace', 'append', 'fail'], 
                       default='replace', 
                       help='导入模式：replace/append/fail (默认: replace)')
    parser.add_argument('--chunksize', type=int, default=50000,
                       help='每次读取的行数（默认: 50000）')
    parser.add_argument('--after-script', type=str, default=None,
                       help='导入完成后要运行的脚本路径（例如：python script.py）')
    return parser.parse_args()

def get_dtype_mapping():
    """定义 SQLAlchemy 数据类型映射，避免数据截断问题"""
    # 所有文本字段使用 TEXT 类型，可能很长的内容使用 LONGTEXT 类型，数值字段使用 BigInteger
    dtype_mapping = {
        'id': BigInteger(),
        'type': Text(),
        'action': Text(),
        'actor_id': BigInteger(),
        'actor_login': Text(),
        'repo_id': BigInteger(),
        'repo_name': Text(),
        'org_id': BigInteger(),
        'org_login': Text(),
        'created_at': Text(),
        'issue_id': BigInteger(),
        'issue_number': BigInteger(),
        'issue_title': LONGTEXT(),  # 标题可能很长
        'body': LONGTEXT(),  # Issue/PR body 可能非常长
        'issue_labels_name': LONGTEXT(),  # JSON 数组可能很长
        'issue_labels_color': LONGTEXT(),
        'issue_labels_default': LONGTEXT(),
        'issue_labels_description': LONGTEXT(),
        'issue_author_id': BigInteger(),
        'issue_author_login': Text(),
        'issue_author_type': Text(),
        'issue_author_association': Text(),
        'issue_assignee_id': BigInteger(),
        'issue_assignee_login': Text(),
        'issue_assignees_login': LONGTEXT(),  # JSON 数组
        'issue_assignees_id': LONGTEXT(),  # JSON 数组
        'issue_created_at': Text(),
        'issue_updated_at': Text(),
        'issue_comments': BigInteger(),
        'issue_closed_at': Text(),
        'issue_comment_id': BigInteger(),
        'issue_comment_created_at': Text(),
        'issue_comment_updated_at': Text(),
        'issue_comment_author_association': Text(),
        'issue_comment_author_id': BigInteger(),
        'issue_comment_author_login': Text(),
        'issue_comment_author_type': Text(),
        'pull_commits': BigInteger(),
        'pull_additions': BigInteger(),
        'pull_deletions': BigInteger(),
        'pull_changed_files': BigInteger(),
        'pull_merged': Integer(),
        'pull_merge_commit_sha': Text(),
        'pull_merged_at': Text(),
        'pull_merged_by_id': BigInteger(),
        'pull_merged_by_login': Text(),
        'pull_merged_by_type': Text(),
        'pull_requested_reviewer_id': BigInteger(),
        'pull_requested_reviewer_login': Text(),
        'pull_requested_reviewer_type': Text(),
        'pull_review_comments': BigInteger(),
        'repo_description': LONGTEXT(),  # 项目描述可能很长
        'repo_size': BigInteger(),
        'repo_stargazers_count': BigInteger(),
        'repo_forks_count': BigInteger(),
        'repo_language': Text(),
        'repo_has_issues': Integer(),
        'repo_has_projects': Integer(),
        'repo_has_downloads': Integer(),
        'repo_has_wiki': Integer(),
        'repo_has_pages': Integer(),
        'repo_license': Text(),
        'repo_default_branch': Text(),
        'repo_created_at': Text(),
        'repo_updated_at': Text(),
        'repo_pushed_at': Text(),
        'pull_review_state': Text(),
        'pull_review_author_association': Text(),
        'pull_review_id': BigInteger(),
        'pull_review_comment_id': BigInteger(),
        'pull_review_comment_path': LONGTEXT(),  # 文件路径可能很长
        'pull_review_comment_position': BigInteger(),
        'pull_review_comment_author_id': BigInteger(),
        'pull_review_comment_author_login': Text(),
        'pull_review_comment_author_type': Text(),
        'pull_review_comment_author_association': Text(),
        'pull_review_comment_created_at': Text(),
        'pull_review_comment_updated_at': Text(),
        'push_id': BigInteger(),
        'push_size': BigInteger(),
        'push_distinct_size': BigInteger(),
        'push_ref': LONGTEXT(),
        'push_head': Text(),
        'push_commits_name': LONGTEXT(),  # JSON 数组
        'push_commits_email': LONGTEXT(),  # JSON 数组
        'push_commits_message': LONGTEXT(),  # 提交消息可能很长，JSON 数组
        'fork_forkee_id': BigInteger(),
        'fork_forkee_full_name': Text(),
        'fork_forkee_owner_id': BigInteger(),
        'fork_forkee_owner_login': Text(),
        'fork_forkee_owner_type': Text(),
        'delete_ref': LONGTEXT(),
        'delete_ref_type': Text(),
        'delete_pusher_type': Text(),
        'create_ref': LONGTEXT(),
        'create_ref_type': Text(),
        'create_master_branch': Text(),
        'create_description': LONGTEXT(),
        'create_pusher_type': Text(),
        'gollum_pages_page_name': LONGTEXT(),  # JSON 数组
        'gollum_pages_title': LONGTEXT(),  # JSON 数组
        'gollum_pages_action': LONGTEXT(),  # JSON 数组
        'member_id': BigInteger(),
        'member_login': Text(),
        'member_type': Text(),
        'release_id': BigInteger(),
        'release_tag_name': Text(),
        'release_target_commitish': Text(),
        'release_name': LONGTEXT(),
        'release_draft': Integer(),
        'release_author_id': BigInteger(),
        'release_author_login': Text(),
        'release_author_type': Text(),
        'release_prerelease': Integer(),
        'release_created_at': Text(),
        'release_published_at': Text(),
        'release_body': LONGTEXT(),  # Release notes 可能非常长
        'release_assets_name': LONGTEXT(),  # JSON 数组
        'release_assets_uploader_login': LONGTEXT(),
        'release_assets_uploader_id': LONGTEXT(),
        'release_assets_content_type': LONGTEXT(),
        'release_assets_state': LONGTEXT(),
        'release_assets_size': LONGTEXT(),
        'release_assets_download_count': LONGTEXT(),
        'commit_comment_id': BigInteger(),
        'commit_comment_author_id': BigInteger(),
        'commit_comment_author_login': Text(),
        'commit_comment_author_type': Text(),
        'commit_comment_author_association': Text(),
        'commit_comment_path': LONGTEXT(),
        'commit_comment_position': Text(),
        'commit_comment_line': Text(),
        'commit_comment_created_at': Text(),
        'commit_comment_updated_at': Text(),
    }
    return dtype_mapping

def count_csv_rows(file_path):
    """快速计算 CSV 文件的总行数（不读入内存）"""
    print("📊 正在计算 CSV 文件总行数...")
    count = 0
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for _ in f:
            count += 1
    return count - 1  # 减去标题行

def import_csv_to_mysql(engine, import_mode, chunksize):
    """将 CSV 文件分块导入到 MySQL 数据库"""
    
    # 检查文件是否存在
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ CSV 文件不存在: {CSV_FILE_PATH}")
        return False
    
    # 获取文件大小
    file_size = os.path.getsize(CSV_FILE_PATH) / (1024 * 1024)  # MB
    print(f"📂 CSV 文件: {CSV_FILE_PATH}")
    print(f"📊 文件大小: {file_size:.2f} MB")
    
    # 计算总行数
    total_csv_rows = count_csv_rows(CSV_FILE_PATH)
    total_chunks = (total_csv_rows + chunksize - 1) // chunksize  # 向上取整
    print(f"📊 CSV 总行数: {total_csv_rows:,} 行")
    print(f"📊 预计分块数: {total_chunks} 块")
    print(f"📋 目标表: {TARGET_TABLE}")
    print(f"📋 导入模式: {import_mode}")
    print(f"📋 分块大小: {chunksize} 行")
    print()
    
    # 获取数据类型映射
    dtype_mapping = get_dtype_mapping()
    
    # 检查表是否已存在
    table_exists = False
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SHOW TABLES LIKE '{TARGET_TABLE}'"))
            table_exists = result.fetchone() is not None
    except Exception:
        table_exists = False
    
    if table_exists and import_mode == 'replace':
        print(f"⚠️  警告: 表 '{TARGET_TABLE}' 已存在，将被覆盖！")
    elif table_exists and import_mode == 'append':
        print(f"ℹ️  表 '{TARGET_TABLE}' 已存在，将追加数据")
    elif table_exists and import_mode == 'fail':
        print(f"❌ 表 '{TARGET_TABLE}' 已存在，导入模式为 'fail'，停止导入")
        return False
    elif not table_exists:
        print(f"ℹ️  表 '{TARGET_TABLE}' 不存在，将创建新表")
    
    print()
    print("🚀 开始导入数据...")
    start_time = datetime.now()
    
    try:
        total_rows = 0
        chunk_count = 0
        stopped_due_to_disk = False
        
        # 使用 chunksize 分块读取大型 CSV 文件
        for chunk in pd.read_csv(CSV_FILE_PATH, chunksize=chunksize, encoding='utf-8', low_memory=False):
            # 每次导入前检查磁盘空间
            is_low, free_gb = is_disk_space_low()
            if is_low:
                print()
                print("=" * 60)
                print(f"⚠️  警告: C盘剩余空间不足！")
                print(f"   当前剩余: {free_gb:.2f} GB")
                print(f"   最小要求: {MIN_DISK_SPACE_GB} GB")
                print(f"   已导入: {total_rows:,} 行")
                print("   导入已自动停止，请清理磁盘空间后重新运行（使用 --mode append）")
                print("=" * 60)
                stopped_due_to_disk = True
                break
            
            chunk_count += 1
            rows_in_chunk = len(chunk)
            total_rows += rows_in_chunk
            
            # 对于第一个块，使用指定的模式；后续块使用 append 模式
            if chunk_count == 1:
                chunk.to_sql(name=TARGET_TABLE, con=engine, if_exists=import_mode, index=False, dtype=dtype_mapping)
            else:
                chunk.to_sql(name=TARGET_TABLE, con=engine, if_exists='append', index=False)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            progress = (total_rows / total_csv_rows) * 100
            remaining_rows = total_csv_rows - total_rows
            speed = total_rows / elapsed if elapsed > 0 else 0
            eta_seconds = remaining_rows / speed if speed > 0 else 0
            eta_minutes = eta_seconds / 60
            free_gb = check_disk_space()
            
            # 进度条
            bar_length = 30
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            print(f"   ✅ 块 {chunk_count}/{total_chunks}: [{bar}] {progress:.1f}% | {total_rows:,}/{total_csv_rows:,} 行 | 耗时: {elapsed:.0f}s | 剩余: {eta_minutes:.1f}分钟 | C盘: {free_gb:.1f}GB")
        
        if stopped_due_to_disk:
            return False
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print()
        print("=" * 50)
        print(f"✅ 导入完成！")
        print(f"📊 总行数: {total_rows}")
        print(f"📊 块数量: {chunk_count}")
        print(f"⏱️  总耗时: {duration:.2f} 秒")
        print(f"📊 平均速度: {total_rows/duration:.0f} 行/秒")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def run_after_script(script_command):
    """导入完成后运行指定的脚本"""
    if not script_command:
        return
    
    print()
    print("=" * 50)
    print(f"🚀 正在运行后续脚本: {script_command}")
    print("=" * 50)
    
    try:
        # 使用 shell=True 来执行命令
        result = subprocess.run(script_command, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            print(f"✅ 后续脚本执行成功！")
        else:
            print(f"⚠️  后续脚本执行完成，返回码: {result.returncode}")
    except Exception as e:
        print(f"❌ 后续脚本执行失败: {e}")

def main():
    # 解析命令行参数
    args = parse_args()
    
    print("=" * 50)
    print("📦 top300_2022_2023.csv 导入工具")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print()
    
    # 显示磁盘空间监控信息
    free_gb = check_disk_space()
    print(f"💾 C盘当前剩余空间: {free_gb:.2f} GB")
    print(f"💾 最小空间阈值: {MIN_DISK_SPACE_GB} GB")
    if args.after_script:
        print(f"📜 完成后将运行: {args.after_script}")
    print()
    
    # 测试数据库连接
    if not test_connection():
        print("\n请先解决数据库连接问题，然后重新运行脚本。")
        return
    
    # 建立 SQLAlchemy 连接
    connection_str = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    engine = create_engine(connection_str)
    
    # 测试 SQLAlchemy 连接
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ SQLAlchemy 连接测试成功！")
        print()
    except Exception as e:
        print(f"❌ SQLAlchemy 连接失败: {e}")
        return
    
    # 执行导入
    success = import_csv_to_mysql(engine, args.mode, args.chunksize)
    
    # 如果导入成功且指定了后续脚本，则运行
    if success and args.after_script:
        run_after_script(args.after_script)

if __name__ == '__main__':
    main()
