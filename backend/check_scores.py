"""检查项目的详细评分数据"""
from app.infrastructure.database import SessionLocal
from app.services.health_service import HealthService

projects = ['AdguardTeam/AdguardFilters', 'airbytehq/airbyte', 'alibaba/nacos', 'angular/angular']

db = SessionLocal()
try:
    service = HealthService(db)
    for project in projects:
        result = service.calculate_health_score(project)
        print(f'=== {project} ===')
        print(f"最终: {result['final_score']:.1f} ({result['grade']})")
        
        g = result['dimensions']['growth']
        print(f"关注度(20%): {g['score']:.1f}")
        print(f"  Star得分: {g.get('star_score', 0):.1f}, Fork得分: {g.get('fork_score', 0):.1f}")
        print(f"  本月Star: {g['details']['star_current_month']}, 前3月均: {g['details']['star_avg_prev_3m']:.1f}")
        print(f"  本月Fork: {g['details']['fork_current_month']}, 前3月均: {g['details']['fork_avg_prev_3m']:.1f}")
        
        a = result['dimensions']['activity']
        print(f"活跃度(40%): {a['score']:.1f}")
        print(f"  Commit趋势: {a.get('commit_trend_score', 0):.1f}, OpenDigger: {a.get('opendigger_score', 0):.1f}")
        print(f"  周均Commit: {a['details']['commit_avg_last_week']:.1f}, 月均: {a['details']['commit_avg_month']:.1f}")
        print(f"  OpenDigger原值: {a['details']['opendigger_activity']:.2f}")
        
        c = result['dimensions']['contribution']
        print(f"贡献度(20%): {c['score']:.1f}")
        print(f"  周均PR: {c['details']['pr_avg_last_week']:.1f}, 月均: {c['details']['pr_avg_month']:.1f}")
        
        code = result['dimensions']['code']
        print(f"代码(20%): {code['score']:.1f}")
        print(f"  additions: {code['details']['pull_additions']}, deletions: {code['details']['pull_deletions']}")
        print()
finally:
    db.close()
