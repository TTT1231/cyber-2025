from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    account: str
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    account: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    registered_at: datetime
    
    class Config:
        from_attributes = True

# 登录相关的模式
class UserLogin(BaseModel):
    """用户登录请求模式"""
    account: str
    password: str

class Token(BaseModel):
    """访问令牌响应模式"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模式"""
    user_id: Optional[int] = None
    account: Optional[str] = None

class ChangePassword(BaseModel):
    """修改密码请求模式"""
    old_password: str
    new_password: str

class UserProfile(BaseModel):
    """用户资料模式"""
    id: int
    username: str
    account: str
    avatar_url: Optional[str] = None
    registered_at: datetime
    
    class Config:
        from_attributes = True