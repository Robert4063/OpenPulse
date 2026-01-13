"""
预计算所有项目的健康度评分
将结果保存到 health_scores.json 文件中
"""
import json
import sys
from datetime import datetime
from sqlalchemy import text
from app.infrastructure.database import engine, SessionLocal
from app.services.health_service import HealthService

def get_all_projects():
    """获取所有项目列表"""
    with engine.connect() as conn:
        result = conn.execute(text('SELECT DISTINCT project FROM stars'))
        return [row[0] for row in result]

def precompute_health_scores():
    """预计算所有项目的健康度评分"""
    print("=" * 60)
    print("🏥 健康度评分预计算工具")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取所有项目
    projects = get_all_projects()
    print(f"\n📊 共 {len(projects)} 个项目需要计算\n")
    
    health_scores = {}
    success_count = 0
    error_count = 0
    
    db = SessionLocal()
    try:
        health_service = HealthService(db)
        
        for i, project in enumerate(projects, 1):
            try:
                # 计算健康度
                result = health_service.calculate_health_score(project)
                
                # 保存结果（使用 owner_repo 格式作为 key）- 包含完整的子指标数据
                project_key = project.replace('/', '_')
                health_scores[project_key] = {
                    'project': project_key,
                    'repo_name': project,
                    'final_score': result['final_score'],
                    'grade': result['grade'],
                    'grade_label': result['grade_label'],
                    'grade_color': result['grade_color'],
                    'dimensions': {
                        'growth': {
                            'name': result['dimensions']['growth']['name'],
                            'weight': result['dimensions']['growth']['weight'],
                            'score': result['dimensions']['growth']['score'],
                            'star_score': result['dimensions']['growth'].get('star_score', 0),
                            'fork_score': result['dimensions']['growth'].get('fork_score', 0),
                            'details': result['dimensions']['growth'].get('details', {})
                        },
                        'activity': {
                            'name': result['dimensions']['activity']['name'],
                            'weight': result['dimensions']['activity']['weight'],
                            'score': result['dimensions']['activity']['score'],
                            'commit_trend_score': result['dimensions']['activity'].get('commit_trend_score', 0),
                            'opendigger_score': result['dimensions']['activity'].get('opendigger_score', 0),
                            'details': result['dimensions']['activity'].get('details', {})
                        },
                        'contribution': {
                            'name': result['dimensions']['contribution']['name'],
                            'weight': result['dimensions']['contribution']['weight'],
                            'score': result['dimensions']['contribution']['score'],
                            'details': result['dimensions']['contribution'].get('details', {})
                        },
                        'code': {
                            'name': result['dimensions']['code']['name'],
                            'weight': result['dimensions']['code']['weight'],
                            'score': result['dimensions']['code']['score'],
                            'details': result['dimensions']['code'].get('details', {})
                        }
                    },
                    'calculated_at': result['calculated_at']
                }
                
                success_count += 1
                grade = result['grade']
                score = result['final_score']
                print(f"[{i:3}/{len(projects)}] ✅ {project}: {grade} ({score:.1f}分)")
                
            except Exception as e:
                error_count += 1
                print(f"[{i:3}/{len(projects)}] ❌ {project}: {str(e)[:50]}")
                # 保存错误项目的默认值
                project_key = project.replace('/', '_')
                health_scores[project_key] = {
                    'project': project_key,
                    'repo_name': project,
                    'final_score': 0,
                    'grade': 'N/A',
                    'grade_label': '无数据',
                    'grade_color': '#6b7280',
                    'dimensions': None,
                    'error': str(e)
                }
    finally:
        db.close()
    
    # 保存到 JSON 文件
    output_file = 'health_scores.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'total_projects': len(projects),
            'success_count': success_count,
            'error_count': error_count,
            'scores': health_scores
        }, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 预计算完成！")
    print(f"   ✅ 成功: {success_count}")
    print(f"   ❌ 失败: {error_count}")
    print(f"   📁 输出文件: {output_file}")
    print("=" * 60)
    
    return health_scores

if __name__ == '__main__':
    precompute_health_scores()