from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from app.db.session import Base

class User(Base):
    # 用户表
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True, comment="用户id")
    username = Column(String(50), nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    account = Column(String(100), unique=True, comment="账号")
    avatar_url = Column(Text, comment="用户头像url")
    registered_at = Column(TIMESTAMP, server_default=func.now(), comment="注册时间")