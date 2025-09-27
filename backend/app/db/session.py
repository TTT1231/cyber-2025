from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
import os
from typing import Generator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME = os.getenv("DB_NAME", "cyber")

# 数据库URL (MySQL+pymysql 驱动)
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# 不包含数据库名的连接URL，用于创建数据库
DATABASE_URL_WITHOUT_DB = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}?charset=utf8mb4"

# 创建数据库引擎 echo=True 会打印所有 SQL 语句，开发调试很有用
engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    future=True,
    pool_pre_ping=True,  # 连接池预检查
    pool_recycle=3600,   # 连接回收时间
    max_overflow=20,     # 最大溢出连接数
    pool_size=10         # 连接池大小
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类（所有表模型都要继承它）
Base = declarative_base()

def create_database_if_not_exists():
    """
    如果数据库不存在则创建数据库
    """
    try:
        # 创建不包含数据库名的引擎
        temp_engine = create_engine(DATABASE_URL_WITHOUT_DB, echo=True)
        
        with temp_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text(f"SHOW DATABASES LIKE '{DB_NAME}'"))
            if not result.fetchone():
                # 创建数据库
                conn.execute(text(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                logger.info(f"数据库 '{DB_NAME}' 创建成功")
            else:
                logger.info(f"数据库 '{DB_NAME}' 已存在")
                
        temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"创建数据库失败: {str(e)}")
        raise

def create_tables():
    """
    创建所有数据表
    """
    try:
        # 导入所有模型以确保它们被注册到Base.metadata
        from app.models.role import Role
        from app.models.chat_sessions import ChatSessions
        from app.models.chat_messages import ChatMessages
        from app.models.user import User
        from app.models.role_settings import RoleSettings
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据表创建成功")
        
    except Exception as e:
        logger.error(f"创建数据表失败: {str(e)}")
        raise

def init_database():
    """
    初始化数据库：创建数据库和表
    """
    try:
        create_database_if_not_exists()
        create_tables()
        logger.info("数据库初始化完成")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False

def test_database_connection():
    """
    测试数据库连接
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone():
                logger.info("数据库连接测试成功")
                return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {str(e)}")
        return False

def get_db() -> Generator:
    """
    获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"数据库会话错误: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()