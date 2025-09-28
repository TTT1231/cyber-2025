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

# 语音消息请求模型
class VoiceMessageRequest(BaseModel):
    text: str
    session_id: int
    role_name: str = "哈利波特"

# 语音消息响应模型
class VoiceMessageResponse(BaseModel):
    audio_url: str
    ai_text: str
    session_id: int
    status: str
    message: str = "语音对话处理成功"