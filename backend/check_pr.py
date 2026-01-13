"""检查 top300 表中的 PR 数据"""
from app.infrastructure.database import engine
from sqlalchemy import text

conn = engine.connect()

# 检查 apache/airflow 的 PullRequestEvent
result = conn.execute(text("""
    SELECT COUNT(*) 
    FROM top300_2022_2023 
    WHERE type='PullRequestEvent' 
    AND repo_name='apache/airflow'
"""))
print("apache/airflow 的 PullRequestEvent 数量:", result.fetchone()[0])

# 检查 top300 表中有多少项目有 PullRequestEvent
result2 = conn.execute(text("""
    SELECT repo_name, COUNT(*) as cnt 
    FROM top300_2022_2023 
    WHERE type='PullRequestEvent' 
    GROUP BY repo_name 
    ORDER BY cnt DESC 
    LIMIT 20
"""))
print("\ntop300 表中有 PullRequestEvent 的项目:")
for r in result2.fetchall():
    print(f"  - {r[0]}: {r[1]}")

conn.close()
