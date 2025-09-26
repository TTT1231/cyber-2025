from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# 消息基础模型
class MessageBase(BaseModel):
    session_id: int
    role: int  # 0-assistant, 1-user
    content: str
    message_type: str = "text"  # text, audio
    metadata: Optional[Dict[str, Any]] = None

# 创建消息请求模型
class MessageCreate(MessageBase):
    pass

# 消息响应模型
class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True