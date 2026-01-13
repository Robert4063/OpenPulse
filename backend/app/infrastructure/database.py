"""
数据库连接池
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 连接前检查连接是否有效
    connect_args={
        'connect_timeout': 60,
        'read_timeout': 120,
        'write_timeout': 120,
        'charset': 'utf8mb4'
    },
    echo=False  # 设置为True可以看到SQL日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（用于FastAPI依赖注入）
    使用方式:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
