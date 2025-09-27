from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, Token, 
    ChangePassword, UserProfile
)
from app.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()

# 获取当前用户的依赖函数
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前认证用户"""
    token = credentials.credentials
    payload = UserService.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌数据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = UserService.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# POST /users/register - 用户注册
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    return UserService.create_user(db=db, user=user)

# POST /users/login - 用户登录
@router.post("/login", response_model=Token)
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = UserService.authenticate_user(db, user_login.account, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)  # 使用固定的30分钟过期时间
    access_token = UserService.create_access_token(
        data={"user_id": user.id, "account": user.account},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# GET /users/profile - 获取当前用户资料
@router.get("/profile", response_model=UserProfile)
def get_user_profile(current_user = Depends(get_current_user)):
    """获取当前用户资料"""
    return current_user

# PUT /users/profile - 更新当前用户资料
@router.put("/profile", response_model=UserProfile)
def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户资料"""
    updated_user = UserService.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return updated_user

# POST /users/change-password - 修改密码
@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    success = UserService.change_password(
        db, current_user.id, password_data.old_password, password_data.new_password
    )
    if success:
        return {"message": "密码修改成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码修改失败"
        )

# POST /users - 创建用户（管理员功能）
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户（管理员功能）"""
    return UserService.create_user(db=db, user=user)

# GET /users - 获取用户列表（管理员功能）
@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有用户列表（管理员功能）"""
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users

# GET /users/{user_id} - 获取单个用户详情（管理员功能）
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取单个用户详情（管理员功能）"""
    user = UserService.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

# PUT /users/{user_id} - 更新用户（管理员功能）
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息（管理员功能）"""
    updated_user = UserService.update_user(db, user_id, user)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return updated_user

# DELETE /users/{user_id} - 删除用户（管理员功能）
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户（管理员功能）"""
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"message": "用户删除成功"}