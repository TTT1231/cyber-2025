from tokenize import String
from sqlalchemy import JSON, TIMESTAMP, Column, Integer, Text, func
from app.db.session import Base

class ChatMessages(Base):
    # 聊天消息表
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="消息id")
    session_id = Column(Integer, nullable=False, comment="会话id")
    query_content = Column(Text,nullable=False,comment="用户提问内容")
    answer_content = Column(Text,nullable=False,comment="模型回答内容")
    message_type = Column(String(20),nullable=False,server_default="text", comment="消息类型，文本/音频等")
    metadata = Column(JSON, nullable=True, comment="消息元数据,例如音频URL(url)、时长(time)、格式(format)等")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment="用户提问创建时间")
    response_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), comment="模型回答返回时间")