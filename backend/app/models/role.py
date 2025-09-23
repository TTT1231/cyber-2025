from sqlalchemy import TIMESTAMP, Column, Integer, Text, func
from app.db.session import Base

class Role(Base):
    # 角色表
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True, comment="id")
    user_id = Column(Integer, nullable=False, comment="创建的用户id 0-系统自带的，用户id-用户创建的")
    name = Column(Integer,nullable=False,comment="角色名")
    avatar_url = Column(Text, comment="角色头像url")
    preset_prompt = Column(Text, comment="角色设定提示词")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
