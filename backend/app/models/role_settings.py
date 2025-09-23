from sqlalchemy import Column, Integer, Text
from app.db.session import Base

class RoleSettings(Base):
    # 角色设定集
    __tablename__="role_settings"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="id")
    role_id = Column(Integer, nullable=False, comment="角色id")
    clip_index = Column(Integer, nullable=False,comment="切片index,每个从1开始")
    total_clips = Column(Integer, nullable=False, comment="总切片数量")
    setting_text = Column(Text, nullable=False, comment="设定内容")