"""检查数据库中的数据格式"""
from app.infrastructure.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT DISTINCT project FROM stars LIMIT 10'))
    print('=== Stars表项目名称格式 ===')
    for row in result:
        print(row[0])
    
    result = conn.execute(text("SELECT project, date, stars_count FROM stars WHERE date >= '2023-03-01' AND date <= '2023-03-31' LIMIT 10"))
    print('\n=== 2023年3月Star数据示例 ===')
    for row in result:
        print(f'{row[0]}: {row[1]} - {row[2]}')
    
    result = conn.execute(text("SELECT project, date, forks_count FROM forks WHERE date >= '2023-03-01' AND date <= '2023-03-31' LIMIT 10"))
    print('\n=== 2023年3月Fork数据示例 ===')
    for row in result:
        print(f'{row[0]}: {row[1]} - {row[2]}')
    
    result = conn.execute(text("SELECT project, date, commit_count FROM commit_activity WHERE date >= '2023-03-01' AND date <= '2023-03-31' LIMIT 10"))
    print('\n=== 2023年3月Commit数据示例 ===')
    for row in result:
        print(f'{row[0]}: {row[1]} - {row[2]}')
    
    result = conn.execute(text("SELECT project, date, pr_count FROM pr_daily WHERE date >= '2023-03-01' AND date <= '2023-03-31' LIMIT 10"))
    print('\n=== 2023年3月PR数据示例 ===')
    for row in result:
        print(f'{row[0]}: {row[1]} - {row[2]}')
