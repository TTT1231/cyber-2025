from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 会话基础模型
class SessionBase(BaseModel):
    role_id: int

# 创建会话请求模型
class SessionCreate(SessionBase):
    pass

# 会话响应模型
class SessionResponse(SessionBase):
    id: int
    last_message_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True