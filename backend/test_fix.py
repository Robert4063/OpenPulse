"""测试修复后的健康度计算"""
from app.infrastructure.database import SessionLocal
from app.services.health_service import HealthService

db = SessionLocal()
try:
    service = HealthService(db)
    result = service.calculate_health_score('AdguardTeam/AdguardFilters')
    print('=== AdguardTeam/AdguardFilters 修复后得分 ===')
    print(f"最终得分: {result['final_score']} ({result['grade']})")
    print(f"关注度增长: {result['dimensions']['growth']['score']}")
    print(f"开发活跃度: {result['dimensions']['activity']['score']}")
    print(f"社区贡献度: {result['dimensions']['contribution']['score']}")
    print(f"代码健康度: {result['dimensions']['code']['score']}")
    print(f"  - pull_additions: {result['dimensions']['code']['details']['pull_additions']}")
    print(f"  - pull_deletions: {result['dimensions']['code']['details']['pull_deletions']}")
finally:
    db.close()
