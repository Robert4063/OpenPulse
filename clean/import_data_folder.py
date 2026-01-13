"""
将 data 文件夹中的 comment_cleaned, fork, issue, star 数据导入到 MySQL 数据库

使用方法:
    python import_data_folder.py                    # 导入所有类型
    python import_data_folder.py --type star        # 只导入 star 数据
    python import_data_folder.py --type fork        # 只导入 fork 数据
    python import_data_folder.py --type issue       # 只导入 issue 数据
    python import_data_folder.py --type comment     # 只导入 comment 数据
    python import_data_folder.py --mode append      # 追加模式

目标数据库:
    - Docker容器: openpulse_data
    - 数据库: openrankdata
    - 端口: 3306
    - 密码: root
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import BigInteger, Text, Integer
from sqlalchemy.dialects.mysql import LONGTEXT
import pymysql
import argparse
import os
import sys
import json
import shutil
from datetime import datetime

# 禁用输出缓冲
sys.stdout.reconfigure(line_buffering=True)

# ====== 磁盘空间监控配置 ======
MIN_DISK_SPACE_GB = 10  # 最小剩余空间（GB）
DISK_TO_MONITOR = "C:\\"  # 监控的磁盘

# ====== 数据库配置 ======
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'openrankdata'

# ====== 数据文件夹配置 ======
DATA_FOLDER = r'D:\openrankdata\data'
DATA_TYPES = {
    'star': {
        'folder': 'star',
        'table': 'stars',
        'file_suffix': '_stars.json'
    },
    'fork': {
        'folder': 'fork',
        'table': 'forks',
        'file_suffix': '_forks.json'
    },
    'issue': {
        'folder': 'issue',
        'table': 'issues',
        'file_suffix': '.json'
    },
    'comment': {
        'folder': 'comment_cleaned',
        'table': 'comments',
        'file_suffix': '.json'
    }
}

def check_disk_space():
    """检查磁盘剩余空间，返回剩余空间（GB）"""
    total, used, free = shutil.disk_usage(DISK_TO_MONITOR)
    free_gb = free / (1024 ** 3)
    return free_gb

def is_disk_space_low():
    """检查磁盘空间是否低于阈值"""
    free_gb = check_disk_space()
    return free_gb < MIN_DISK_SPACE_GB, free_gb

def test_connection():
    """测试数据库连接并创建数据库（如果不存在）"""
    try:
        test_conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✅ MySQL 服务器连接成功！")
        
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
            print("1. Docker MySQL 容器 (openpulse_data) 未启动")
            print("   - 检查容器状态: docker ps -a")
            print("   - 启动容器: docker start openpulse_data")
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
    parser = argparse.ArgumentParser(description='导入 data 文件夹数据到 MySQL 数据库')
    parser.add_argument('--type', choices=['star', 'fork', 'issue', 'comment', 'all'], 
                       default='all', 
                       help='数据类型：star/fork/issue/comment/all (默认: all)')
    parser.add_argument('--mode', choices=['replace', 'append', 'fail'], 
                       default='replace', 
                       help='导入模式：replace/append/fail (默认: replace)')
    return parser.parse_args()

def process_star_fork_file(file_path, data_type):
    """处理 star 或 fork 类型的 JSON 文件，展开为多行数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    project = data.get('project', os.path.basename(file_path).replace('_stars.json', '').replace('_forks.json', '').replace('_', '/'))
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    
    if data_type == 'star':
        total_count = data.get('total_stargazers', 0)
        daily_data = data.get('daily_stars', {})
        count_field = 'stars_count'
        total_field = 'total_stargazers'
    else:  # fork
        total_count = data.get('total_forks', 0)
        daily_data = data.get('daily_forks', {})
        count_field = 'forks_count'
        total_field = 'total_forks'
    
    rows = []
    for date, count in daily_data.items():
        rows.append({
            'project': project,
            'date': date,
            count_field: count,
            total_field: total_count
        })
    
    return pd.DataFrame(rows)

def process_issue_file(file_path):
    """处理 issue 类型的 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 从文件名提取项目名
    file_name = os.path.basename(file_path)
    project = file_name.replace('.json', '').replace('_', '/')
    
    rows = []
    for issue in data:
        rows.append({
            'project': project,
            'title': issue.get('title', ''),
            'body': issue.get('body', ''),
            'state': issue.get('state', ''),
            'number': issue.get('number', 0),
            'created_at': issue.get('created_at', ''),
            'closed_at': issue.get('closed_at', ''),
            'labels': json.dumps(issue.get('labels', []), ensure_ascii=False),
            'author_association': issue.get('author_association', ''),
            'user': issue.get('user', ''),
            'html_url': issue.get('html_url', '')
        })
    
    return pd.DataFrame(rows)

def extract_username(user_field):
    """从 user 字段提取用户名，user 可能是字符串或字典"""
    if user_field is None:
        return ''
    if isinstance(user_field, str):
        return user_field
    if isinstance(user_field, dict):
        return user_field.get('login', '')
    return str(user_field)

def process_comment_file(file_path):
    """处理 comment_cleaned 类型的 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 从文件名提取项目名
    file_name = os.path.basename(file_path)
    project = file_name.replace('.json', '').replace('_', '/', 1)
    
    source_file = data.get('source_file', '')
    total_comments = data.get('total_comments', 0)
    
    rows = []
    for issue_data in data.get('issues', []):
        issue_url = issue_data.get('issue_url', '')
        for comment in issue_data.get('comments', []):
            rows.append({
                'project': project,
                'issue_url': issue_url,
                'comment_id': comment.get('id', 0),
                'body': comment.get('body', ''),
                'user': extract_username(comment.get('user')),
                'created_at': comment.get('created_at', ''),
                'updated_at': comment.get('updated_at', ''),
                'html_url': comment.get('html_url', '')
            })
    
    return pd.DataFrame(rows)

def get_dtype_mapping(data_type):
    """获取不同数据类型的 SQLAlchemy 类型映射"""
    if data_type == 'star':
        return {
            'project': Text(),
            'date': Text(),
            'stars_count': Integer(),
            'total_stargazers': BigInteger()
        }
    elif data_type == 'fork':
        return {
            'project': Text(),
            'date': Text(),
            'forks_count': Integer(),
            'total_forks': BigInteger()
        }
    elif data_type == 'issue':
        return {
            'project': Text(),
            'title': LONGTEXT(),
            'body': LONGTEXT(),
            'state': Text(),
            'number': BigInteger(),
            'created_at': Text(),
            'closed_at': Text(),
            'labels': LONGTEXT(),
            'author_association': Text(),
            'user': Text(),
            'html_url': Text()
        }
    elif data_type == 'comment':
        return {
            'project': Text(),
            'issue_url': Text(),
            'comment_id': BigInteger(),
            'body': LONGTEXT(),
            'user': Text(),
            'created_at': Text(),
            'updated_at': Text(),
            'html_url': Text()
        }
    return {}

def import_data_type(engine, data_type, import_mode):
    """导入指定类型的数据"""
    config = DATA_TYPES[data_type]
    folder_path = os.path.join(DATA_FOLDER, config['folder'])
    table_name = config['table']
    
    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return False
    
    # 获取所有 JSON 文件
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    if not files:
        print(f"❌ 文件夹 {folder_path} 中没有 JSON 文件")
        return False
    
    print(f"\n📂 正在导入 {data_type} 数据...")
    print(f"   文件夹: {folder_path}")
    print(f"   文件数: {len(files)}")
    print(f"   目标表: {table_name}")
    print(f"   导入模式: {import_mode}")
    
    dtype_mapping = get_dtype_mapping(data_type)
    start_time = datetime.now()
    total_rows = 0
    processed_files = 0
    all_data = []
    
    for i, filename in enumerate(files):
        # 检查磁盘空间
        is_low, free_gb = is_disk_space_low()
        if is_low:
            print(f"\n⚠️  C盘空间不足 ({free_gb:.2f}GB < {MIN_DISK_SPACE_GB}GB)，停止导入")
            break
        
        file_path = os.path.join(folder_path, filename)
        
        try:
            # 根据数据类型处理文件
            if data_type in ['star', 'fork']:
                df = process_star_fork_file(file_path, data_type)
            elif data_type == 'issue':
                df = process_issue_file(file_path)
            elif data_type == 'comment':
                df = process_comment_file(file_path)
            else:
                continue
            
            if df.empty:
                continue
            
            all_data.append(df)
            total_rows += len(df)
            processed_files += 1
            
            # 进度显示
            progress = ((i + 1) / len(files)) * 100
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"   [{i+1}/{len(files)}] {progress:.1f}% | {filename} | {len(df)} 行 | C盘: {check_disk_space():.1f}GB")
            
        except Exception as e:
            print(f"   ❌ 处理 {filename} 失败: {e}")
            continue
    
    # 合并所有数据并写入数据库
    if all_data:
        print(f"\n   📊 合并 {len(all_data)} 个文件的数据...")
        combined_df = pd.concat(all_data, ignore_index=True)
        
        print(f"   📊 写入数据库 ({total_rows:,} 行)...")
        combined_df.to_sql(name=table_name, con=engine, if_exists=import_mode, index=False, dtype=dtype_mapping)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ {data_type} 导入完成！")
        print(f"      文件数: {processed_files}")
        print(f"      总行数: {total_rows:,}")
        print(f"      耗时: {elapsed:.1f} 秒")
        return True
    else:
        print(f"   ⚠️  没有数据可导入")
        return False

def main():
    args = parse_args()
    
    print("=" * 60)
    print("📦 Data 文件夹导入工具")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 显示配置信息
    print(f"💾 C盘剩余空间: {check_disk_space():.2f} GB")
    print(f"💾 最小空间阈值: {MIN_DISK_SPACE_GB} GB")
    print(f"📋 数据类型: {args.type}")
    print(f"📋 导入模式: {args.mode}")
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
    except Exception as e:
        print(f"❌ SQLAlchemy 连接失败: {e}")
        return
    
    # 确定要导入的数据类型
    if args.type == 'all':
        types_to_import = ['star', 'fork', 'issue', 'comment']
    else:
        types_to_import = [args.type]
    
    # 导入数据
    start_time = datetime.now()
    success_count = 0
    
    for data_type in types_to_import:
        # 对于第一种类型使用指定的模式，后续使用 append（如果是 all 模式）
        mode = args.mode if data_type == types_to_import[0] else 'append' if args.mode == 'replace' else args.mode
        if import_data_type(engine, data_type, args.mode):
            success_count += 1
    
    # 汇总
    elapsed = (datetime.now() - start_time).total_seconds()
    print()
    print("=" * 60)
    print(f"✅ 导入完成！")
    print(f"   成功导入: {success_count}/{len(types_to_import)} 种数据类型")
    print(f"   总耗时: {elapsed:.1f} 秒")
    print("=" * 60)

if __name__ == '__main__':
    main()
