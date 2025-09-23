from tokenize import String
from sqlalchemy import JSON, TIMESTAMP, Column, Integer, Text, func
from app.db.session import Base

class ChatMessages(Base):
    # 聊天消息表
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="消息id")
    session_id = Column(Integer, nullable=False, comment="会话id")
    role = Column(Integer, nullable=False,comment="0-assistant,")
    content = Column(Text,nullable=False,comment="消息内容")
    message_type = Column(String(20),nullable=False,server_default="text", comment="消息类型，文本/音频等")
    metadata = Column(JSON, nullable=True, comment="消息元数据,例如音频URL(url)、时长(time)、格式(format)等")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment="创建时间")