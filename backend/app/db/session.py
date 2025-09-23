from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

# 数据库URL (MySQL+pymysql 驱动)
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/cyber?charset=utf8mb4"

# 创建数据库引擎 echo=True 会打印所有 SQL 语句，开发调试很有用
engine = create_engine(DATABASE_URL, echo=True, future=True)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类（所有表模型都要继承它）
Base = declarative_base()

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()