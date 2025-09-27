from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional

from app.db.session import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.services.role_service import RoleService

router = APIRouter()

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    """获取角色服务实例"""
    return RoleService(db)

@router.get("/", response_model=List[RoleResponse])
def get_roles(
    skip: int = 0, 
    limit: int = 100, 
    user_id: Optional[int] = None,
    role_service: RoleService = Depends(get_role_service)
):
    """
    获取角色列表
    
    Args:
        skip: 跳过的记录数
        limit: 限制返回的记录数  
        user_id: 可选的用户ID筛选
        role_service: 角色服务实例
        
    Returns:
        角色列表
    """
    try:
        roles = role_service.get_roles(skip=skip, limit=limit, user_id=user_id)
        return [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.avatar_url,  # 临时映射
                voice_sample_url=role.preset_prompt,  # 临时映射
                created_at=role.created_at
            ) for role in roles
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色列表失败: {str(e)}"
        )

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role: RoleCreate, 
    user_id: int = 0,  # 默认系统角色
    role_service: RoleService = Depends(get_role_service)
):
    """
    创建新角色
    
    Args:
        role: 角色创建数据
        user_id: 创建者用户ID
        role_service: 角色服务实例
        
    Returns:
        创建的角色信息
    """
    try:
        db_role = role_service.create_role(role, user_id=user_id)
        return RoleResponse(
            id=db_role.id,
            name=db_role.name,
            description=db_role.avatar_url,  # 临时映射
            voice_sample_url=db_role.preset_prompt,  # 临时映射
            created_at=db_role.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建角色失败: {str(e)}"
        )

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int, 
    role_service: RoleService = Depends(get_role_service)
):
    """
    获取指定角色
    
    Args:
        role_id: 角色ID
        role_service: 角色服务实例
        
    Returns:
        角色信息
    """
    try:
        db_role = role_service.get_role_by_id(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID {role_id} 不存在"
            )
        
        return RoleResponse(
            id=db_role.id,
            name=db_role.name,
            description=db_role.avatar_url,  # 临时映射
            voice_sample_url=db_role.preset_prompt,  # 临时映射
            created_at=db_role.created_at
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色失败: {str(e)}"
        )

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int, 
    role: RoleUpdate, 
    user_id: Optional[int] = None,
    role_service: RoleService = Depends(get_role_service)
):
    """
    更新角色
    
    Args:
        role_id: 角色ID
        role: 角色更新数据
        user_id: 操作用户ID，用于权限检查
        role_service: 角色服务实例
        
    Returns:
        更新后的角色信息
    """
    try:
        db_role = role_service.update_role(role_id, role, user_id=user_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID {role_id} 不存在"
            )
        
        return RoleResponse(
            id=db_role.id,
            name=db_role.name,
            description=db_role.avatar_url,  # 临时映射
            voice_sample_url=db_role.preset_prompt,  # 临时映射
            created_at=db_role.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新角色失败: {str(e)}"
        )

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int, 
    user_id: Optional[int] = None,
    role_service: RoleService = Depends(get_role_service)
):
    """
    删除角色
    
    Args:
        role_id: 角色ID
        user_id: 操作用户ID，用于权限检查
        role_service: 角色服务实例
    """
    try:
        success = role_service.delete_role(role_id, user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色ID {role_id} 不存在"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除角色失败: {str(e)}"
        )

@router.get("/system/roles", response_model=List[RoleResponse])
def get_system_roles(role_service: RoleService = Depends(get_role_service)):
    """
    获取系统预设角色
    
    Args:
        role_service: 角色服务实例
        
    Returns:
        系统角色列表
    """
    try:
        roles = role_service.get_system_roles()
        return [
            RoleResponse(
                id=role.id,
                name=role.name,
                description=role.avatar_url,  # 临时映射
                voice_sample_url=role.preset_prompt,  # 临时映射
                created_at=role.created_at
            ) for role in roles
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统角色失败: {str(e)}"
        )
