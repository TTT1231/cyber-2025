from fastapi import APIRouter

router = APIRouter()
# POST   /roles        # 创建角色
# @router.post("/")
# def create_role(role:dict)

# GET    /roles        # 获取角色列表
@router.get("/")
def get_roles()
# GET    /roles/{id}   # 获取单个角色详情
# PUT    /roles/{id}   # 更新角色
# DELETE /roles/{id}   # 删除角色
