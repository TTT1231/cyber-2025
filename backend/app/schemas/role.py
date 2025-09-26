from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 角色基础模型
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    voice_sample_url: Optional[str] = None

# 创建角色请求模型
class RoleCreate(RoleBase):
    pass

# 更新角色请求模型
class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    voice_sample_url: Optional[str] = None

# 角色响应模型
class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
