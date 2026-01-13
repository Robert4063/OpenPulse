"""
将 commit_activity 和 pr_daily 数据导入到 MySQL 数据库

使用方法:
    python import_commits_prs.py                    # 导入所有类型
    python import_commits_prs.py --type commit      # 只导入 commit 数据
    python import_commits_prs.py --type pr          # 只导入 PR 数据
    python import_commits_prs.py --mode append      # 追加模式

目标数据库:
    - Docker容器: openpulse_data
    - 数据库: openrankdata
    - 端口: 3306
    - 密码: root
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import BigInteger, Text, Integer, Date
import pymysql
import argparse
import os
import sys
import json
import shutil
from datetime import datetime

# 禁用输出缓冲
sys.stdout.reconfigure(line_buffering=True)

# ====== 数据库配置 ======
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'openrankdata'

# ====== 数据文件夹配置 ======
DATA_BASE_PATH = r'D:\openrankdata\crawls\data'

# 数据类型配置
DATA_CONFIGS = {
    'commit': {
        'folder': 'commit_activity',
        'table': 'commit_activity',
        'file_suffix': '_commits.json',
        'daily_key': 'daily_commits',
        'count_field': 'commit_count'
    },
    'pr': {
        'folder': 'pr_daily',
        'table': 'pr_daily',
        'file_suffix': '_prs.json',
        'daily_key': 'daily_prs',
        'count_field': 'pr_count'
    }
}

# 磁盘空间阈值 (GB)
MIN_DISK_SPACE_GB = 10


def get_disk_free_space_gb(path='C:\\'):
    """获取磁盘剩余空间 (GB)"""
    total, used, free = shutil.disk_usage(path)
    return free / (1024 ** 3)


def check_disk_space():
    """检查磁盘空间是否足够"""
    free_gb = get_disk_free_space_gb()
    if free_gb < MIN_DISK_SPACE_GB:
        print(f"\n⚠️ 警告: C盘剩余空间不足 ({free_gb:.1f}GB < {MIN_DISK_SPACE_GB}GB)")
        print("⏸️ 导入已暂停，请清理磁盘空间后重新运行")
        return False
    return True


def test_connection():
    """测试数据库连接并创建数据库（如果不存在）"""
    try:
        test_conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        print("✅ MySQL 服务器连接成功！")
        
        cursor = test_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
        if cursor.fetchone():
            print(f"✅ 数据库 '{DB_NAME}' 已存在")
        
        cursor.close()
        test_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def parse_json_file(file_path, config):
    """解析 JSON 文件并转换为 DataFrame"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    project = data.get('project', '')
    daily_data = data.get(config['daily_key'], {})
    
    # 转换为记录列表
    records = []
    for date_str, count in daily_data.items():
        records.append({
            'project': project,
            'date': date_str,
            config['count_field']: count
        })
    
    return records


def import_data_type(engine, data_type, import_mode):
    """导入指定类型的数据"""
    config = DATA_CONFIGS[data_type]
    folder_path = os.path.join(DATA_BASE_PATH, config['folder'])
    
    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return False
    
    # 获取所有 JSON 文件
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    total_files = len(json_files)
    
    if total_files == 0:
        print(f"⚠️ 文件夹中没有 JSON 文件: {folder_path}")
        return False
    
    print(f"\n📂 正在导入 {data_type} 数据...")
    print(f"   文件夹: {folder_path}")
    print(f"   文件数: {total_files}")
    print(f"   目标表: {config['table']}")
    print(f"   导入模式: {import_mode}")
    
    all_records = []
    start_time = datetime.now()
    
    for idx, filename in enumerate(json_files, 1):
        # 检查磁盘空间
        if idx % 10 == 0 and not check_disk_space():
            return False
        
        file_path = os.path.join(folder_path, filename)
        try:
            records = parse_json_file(file_path, config)
            all_records.extend(records)
            
            free_gb = get_disk_free_space_gb()
            progress = (idx / total_files) * 100
            print(f"   [{idx}/{total_files}] {progress:.1f}% | {filename} | {len(records)} 行 | C盘: {free_gb:.1f}GB")
            
        except Exception as e:
            print(f"   ❌ 处理 {filename} 失败: {e}")
            continue
    
    if not all_records:
        print(f"⚠️ 没有有效数据可导入")
        return False
    
    # 转换为 DataFrame
    print(f"\n   📊 合并 {len(json_files)} 个文件的数据...")
    df = pd.DataFrame(all_records)
    
    # 定义数据类型
    dtype_mapping = {
        'project': Text(),
        'date': Text(),
        config['count_field']: Integer()
    }
    
    # 写入数据库
    print(f"   📊 写入数据库 ({len(df)} 行)...")
    df.to_sql(
        name=config['table'],
        con=engine,
        if_exists=import_mode,
        index=False,
        dtype=dtype_mapping
    )
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"   ✅ {data_type} 导入完成！")
    print(f"      文件数: {len(json_files)}")
    print(f"      总行数: {len(df)}")
    print(f"      耗时: {elapsed:.1f} 秒")
    
    return True


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='导入 commit_activity 和 pr_daily 数据到 MySQL')
    parser.add_argument('--type', choices=['commit', 'pr', 'all'],
                       default='all',
                       help='数据类型：commit/pr/all (默认: all)')
    parser.add_argument('--mode', choices=['replace', 'append', 'fail'],
                       default='replace',
                       help='导入模式：replace/append/fail (默认: replace)')
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 60)
    print("📦 Commit/PR 数据导入工具")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 显示磁盘空间
    free_gb = get_disk_free_space_gb()
    print(f"💾 C盘剩余空间: {free_gb:.2f} GB")
    print(f"💾 最小空间阈值: {MIN_DISK_SPACE_GB} GB")
    print(f"📋 数据类型: {args.type}")
    print(f"📋 导入模式: {args.mode}")
    print()
    
    # 检查磁盘空间
    if not check_disk_space():
        return
    
    # 测试数据库连接
    if not test_connection():
        print("\n请先解决数据库连接问题，然后重新运行脚本。")
        return
    
    # 建立 SQLAlchemy 连接
    connection_str = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    engine = create_engine(connection_str)
    
    # 测试连接
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ SQLAlchemy 连接测试成功！")
    except Exception as e:
        print(f"❌ SQLAlchemy 连接失败: {e}")
        return
    
    # 确定要导入的数据类型
    if args.type == 'all':
        data_types = ['commit', 'pr']
    else:
        data_types = [args.type]
    
    # 导入数据
    total_start = datetime.now()
    success_count = 0
    
    for data_type in data_types:
        if import_data_type(engine, data_type, args.mode):
            success_count += 1
    
    # 总结
    total_elapsed = (datetime.now() - total_start).total_seconds()
    print()
    print("=" * 60)
    print("📊 导入完成!")
    print(f"   成功: {success_count}/{len(data_types)} 个数据类型")
    print(f"   总耗时: {total_elapsed:.1f} 秒")
    print("=" * 60)


if __name__ == '__main__':
    main()
