from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from app.db.session import get_db


class RoleService:
    """角色服务层，处理角色相关的业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_role(self, role_data: RoleCreate, user_id: int = 0) -> Role:
        """
        创建新角色
        
        Args:
            role_data: 角色创建数据
            user_id: 创建者用户ID，默认0表示系统角色
            
        Returns:
            创建的角色对象
            
        Raises:
            ValueError: 当角色名已存在时
            SQLAlchemyError: 数据库操作异常
        """
        try:
            # 检查角色名是否已存在
            existing_role = self.db.query(Role).filter(Role.name == role_data.name).first()
            if existing_role:
                raise ValueError(f"角色名 '{role_data.name}' 已存在")
            
            # 创建新角色
            db_role = Role(
                user_id=user_id,
                name=role_data.name,
                avatar_url=role_data.description,  # 注意：数据库字段与schema不完全匹配
                preset_prompt=role_data.voice_sample_url,  # 临时映射，需要调整数据库结构
                created_at=datetime.now()
            )
            
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
            
            return db_role
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise SQLAlchemyError(f"创建角色失败: {str(e)}")
    
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """
        根据ID获取角色
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色对象或None
        """
        try:
            return self.db.query(Role).filter(Role.id == role_id).first()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"获取角色失败: {str(e)}")
    
    def get_roles(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Role]:
        """
        获取角色列表
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            user_id: 可选的用户ID筛选
            
        Returns:
            角色列表
        """
        try:
            query = self.db.query(Role)
            
            # 如果指定了用户ID，则筛选该用户的角色
            if user_id is not None:
                query = query.filter(Role.user_id == user_id)
            
            return query.offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"获取角色列表失败: {str(e)}")
    
    def update_role(self, role_id: int, role_data: RoleUpdate, user_id: Optional[int] = None) -> Optional[Role]:
        """
        更新角色信息
        
        Args:
            role_id: 角色ID
            role_data: 更新数据
            user_id: 操作用户ID，用于权限检查
            
        Returns:
            更新后的角色对象或None
            
        Raises:
            ValueError: 当角色不存在或无权限时
            SQLAlchemyError: 数据库操作异常
        """
        try:
            # 获取现有角色
            db_role = self.get_role_by_id(role_id)
            if not db_role:
                raise ValueError(f"角色ID {role_id} 不存在")
            
            # 权限检查：只有角色创建者或系统管理员可以修改
            if user_id is not None and db_role.user_id != user_id and user_id != 0:
                raise ValueError("无权限修改此角色")
            
            # 检查角色名是否与其他角色冲突
            if role_data.name and role_data.name != db_role.name:
                existing_role = self.db.query(Role).filter(
                    Role.name == role_data.name,
                    Role.id != role_id
                ).first()
                if existing_role:
                    raise ValueError(f"角色名 '{role_data.name}' 已存在")
            
            # 更新字段
            update_data = role_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field == "name":
                    db_role.name = value
                elif field == "description":
                    db_role.avatar_url = value  # 临时映射
                elif field == "voice_sample_url":
                    db_role.preset_prompt = value  # 临时映射
            
            self.db.commit()
            self.db.refresh(db_role)
            
            return db_role
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise SQLAlchemyError(f"更新角色失败: {str(e)}")
    
    def delete_role(self, role_id: int, user_id: Optional[int] = None) -> bool:
        """
        删除角色
        
        Args:
            role_id: 角色ID
            user_id: 操作用户ID，用于权限检查
            
        Returns:
            删除成功返回True，角色不存在返回False
            
        Raises:
            ValueError: 当无权限删除时
            SQLAlchemyError: 数据库操作异常
        """
        try:
            # 获取现有角色
            db_role = self.get_role_by_id(role_id)
            if not db_role:
                return False
            
            # 权限检查：只有角色创建者或系统管理员可以删除
            if user_id is not None and db_role.user_id != user_id and user_id != 0:
                raise ValueError("无权限删除此角色")
            
            # 检查是否有关联的会话（可选的业务规则）
            # TODO: 如果需要，可以添加检查是否有活跃会话使用此角色
            
            self.db.delete(db_role)
            self.db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise SQLAlchemyError(f"删除角色失败: {str(e)}")
    
    def get_system_roles(self) -> List[Role]:
        """
        获取系统预设角色（user_id=0）
        
        Returns:
            系统角色列表
        """
        try:
            return self.db.query(Role).filter(Role.user_id == 0).all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"获取系统角色失败: {str(e)}")
    
    def validate_role_exists(self, role_id: int) -> bool:
        """
        验证角色是否存在
        
        Args:
            role_id: 角色ID
            
        Returns:
            存在返回True，不存在返回False
        """
        return self.get_role_by_id(role_id) is not None


def get_role_service(db: Session = None) -> RoleService:
    """
    获取角色服务实例
    
    Args:
        db: 数据库会话，如果不提供则使用默认会话
        
    Returns:
        角色服务实例
    """
    if db is None:
        db = next(get_db())
    return RoleService(db)