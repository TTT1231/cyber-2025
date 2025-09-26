from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 用户基础模型
class UserBase(BaseModel):
    username: str
    account: str
    avatar_url: Optional[str] = None

# 创建用户请求模型
class UserCreate(UserBase):
    password: str

# 更新用户请求模型
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None

# 用户响应模型
class UserResponse(UserBase):
    id: int
    registered_at: datetime
    
    class Config:
        from_attributes = True