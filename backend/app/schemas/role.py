from pydantic import BaseModel

# 基础模型（返回时用）
class RoleBase(BaseModel):
    id:int
    user_id: int
    name: str
    avatar_url: str
