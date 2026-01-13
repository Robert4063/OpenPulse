"""
测试后端是否可以正常运行
"""
import sys
import traceback

def test_imports():
    """测试所有模块导入"""
    print("=" * 50)
    print("测试模块导入...")
    print("=" * 50)
    
    try:
        print("1. 导入config...")
        from app.config import settings
        print(f"   ✓ Config loaded: DB={settings.DB_NAME}, Host={settings.DB_HOST}")
    except Exception as e:
        print(f"   ✗ Config导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("2. 导入database...")
        from app.infrastructure.database import get_db, engine
        print("   ✓ Database模块导入成功")
    except Exception as e:
        print(f"   ✗ Database导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("3. 导入models...")
        from app.models.schemas import ProjectInfo, TrendData, ProjectSummary
        print("   ✓ Models导入成功")
    except Exception as e:
        print(f"   ✗ Models导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("4. 导入repository...")
        from app.repository.github_repo import GitHubRepository
        print("   ✓ Repository导入成功")
    except Exception as e:
        print(f"   ✗ Repository导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("5. 导入API...")
        from app.api import search, stats
        print("   ✓ API模块导入成功")
    except Exception as e:
        print(f"   ✗ API导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        print("6. 导入main应用...")
        from main import app
        print("   ✓ Main应用导入成功")
    except Exception as e:
        print(f"   ✗ Main应用导入失败: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("✓ 所有模块导入成功！")
    print("=" * 50)
    return True

def test_database_connection():
    """测试数据库连接"""
    print("\n" + "=" * 50)
    print("测试数据库连接...")
    print("=" * 50)
    
    try:
        from app.infrastructure.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✓ 数据库连接成功！")
                
                # 检查表
                tables = conn.execute(text("SHOW TABLES")).fetchall()
                print(f"✓ 数据库表: {[t[0] for t in tables]}")
                return True
            else:
                print("✗ 数据库连接测试失败")
                return False
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        print("\n提示：请确保Docker MySQL容器正在运行")
        print("   docker ps | grep mysql")
        return False

def test_api():
    """测试API查询"""
    print("\n" + "=" * 50)
    print("测试API查询...")
    print("=" * 50)
    
    try:
        from app.infrastructure.database import SessionLocal
        from app.repository.github_repo import GitHubRepository
        
        db = SessionLocal()
        repo = GitHubRepository(db)
        
        # 测试搜索
        items, total = repo.search_projects(limit=5)
        print(f"✓ 搜索测试: 找到 {total} 个项目")
        if items:
            print(f"  示例项目: {items[0]['repo_name']}")
        
        # 测试趋势
        if items:
            project_key = items[0]['project_key']
            trend = repo.get_stars_trend(project_key)
            print(f"✓ 趋势测试: 获取到 {len(trend['labels'])} 个数据点")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ API测试失败: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("OpenPulse 后端测试")
    print("=" * 50 + "\n")
    
    # 测试导入
    if not test_imports():
        print("\n❌ 模块导入测试失败，请检查错误信息")
        sys.exit(1)
    
    # 测试数据库连接
    db_ok = test_database_connection()
    
    # 测试API
    api_ok = False
    if db_ok:
        api_ok = test_api()
    
    print("\n" + "=" * 50)
    if db_ok and api_ok:
        print("✓ 所有测试通过！后端可以正常运行")
        print("\n启动命令：")
        print("  python main.py")
        print("  或")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    elif db_ok:
        print("⚠️  数据库连接成功，但API测试失败")
    else:
        print("⚠️  模块导入成功，但数据库连接失败")
        print("   后端可以启动，但需要数据库连接才能正常工作")
    print("=" * 50 + "\n")
