"""
创建数据库索引脚本
用于提高查询性能
运行方式: python create_indexes.py
"""
import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'openrankdata',
    'charset': 'utf8mb4'
}

INDEXES = [
    ("stars", "idx_stars_project", "project(255)"),
    ("stars", "idx_stars_project_date", "project(100), date(10)"),
    ("stars", "idx_stars_date", "date(10)"),
    
    ("forks", "idx_forks_project", "project(255)"),
    ("forks", "idx_forks_project_date", "project(100), date(10)"),
    ("forks", "idx_forks_date", "date(10)"),
    
    ("commit_activity", "idx_commit_project", "project(255)"),
    ("commit_activity", "idx_commit_project_date", "project(100), date(10)"),
    ("commit_activity", "idx_commit_date", "date(10)"),
    
    ("pr_daily", "idx_pr_project", "project(255)"),
    ("pr_daily", "idx_pr_project_date", "project(100), date(10)"),
    ("pr_daily", "idx_pr_date", "date(10)"),
    
    ("top300_2022_2023", "idx_top300_repo_name", "repo_name(255)"),
    ("top300_2022_2023", "idx_top300_type", "type(50)"),
    ("top300_2022_2023", "idx_top300_repo_type", "repo_name(100), type(50)"),
    
    ("comments", "idx_comments_project", "project(255)"),
]


def check_index_exists(cursor, table, index_name):
    try:
        cursor.execute(f"SHOW INDEX FROM `{table}` WHERE Key_name = %s", (index_name,))
        return cursor.fetchone() is not None
    except:
        return False


def check_table_exists(cursor, table):
    cursor.execute(f"SHOW TABLES LIKE %s", (table,))
    return cursor.fetchone() is not None


def create_indexes():
    print("=" * 60)
    print("📊 数据库索引创建工具 v2")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ 数据库连接成功！")
        print()
        
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for table, index_name, columns in INDEXES:
            try:
                if not check_table_exists(cursor, table):
                    print(f"⏭️  跳过 {table}.{index_name} - 表不存在")
                    skip_count += 1
                    continue
                
                if check_index_exists(cursor, table, index_name):
                    print(f"⏭️  跳过 {table}.{index_name} - 索引已存在")
                    skip_count += 1
                    continue
                
                sql = f"CREATE INDEX `{index_name}` ON `{table}` ({columns})"
                print(f"🔧 正在创建 {table}.{index_name}...")
                cursor.execute(sql)
                conn.commit()
                print(f"   ✅ 创建成功！")
                success_count += 1
                
            except pymysql.err.OperationalError as e:
                error_code = e.args[0]
                if error_code == 1061:  # Duplicate key name
                    print(f"⏭️  跳过 {table}.{index_name} - 索引已存在")
                    skip_count += 1
                else:
                    print(f"   ❌ 创建 {table}.{index_name} 失败: {e}")
                    fail_count += 1
                continue
            except Exception as e:
                print(f"   ❌ 创建 {table}.{index_name} 失败: {e}")
                fail_count += 1
                continue
        
        cursor.close()
        conn.close()
        print()
        print("=" * 60)
        print("📊 索引创建完成！")
        print(f"   ✅ 成功: {success_count}")
        print(f"   ⏭️  跳过: {skip_count}")
        print(f"   ❌ 失败: {fail_count}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        
if __name__ == '__main__':
    create_indexes()
