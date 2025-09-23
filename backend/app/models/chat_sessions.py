from sqlalchemy import TIMESTAMP, Column, Integer, func
from app.db.session import Base

class ChatSessions(Base):
    # 聊天会话表
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="会话id")
    user_id = Column(Integer, nullable=False, comment="用户id")
    role_id = Column(Integer, nullable=False, comment="角色id")
    last_message_at = Column(TIMESTAMP, nullable=True, comment="最近一次对话时间")
    created_at = Column(TIMESTAMP,nullable=False,server_default=func.now(), comment="创建时间")