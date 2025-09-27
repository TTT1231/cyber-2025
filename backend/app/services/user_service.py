from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# 密码加密配置 - 使用更兼容的配置
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

# JWT配置
SECRET_KEY = "your-secret-key-here"  # 在生产环境中应该从环境变量获取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserService:
    """用户服务类"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            # 如果bcrypt验证失败，尝试SHA256验证（用于备用哈希）
            import hashlib
            return hashlib.sha256(plain_password.encode('utf-8')).hexdigest() == hashed_password
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        try:
            # 确保密码是字符串类型
            if not isinstance(password, str):
                password = str(password)
            
            # 将密码转换为字节并限制长度
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                # 直接截断到72字节
                password_bytes = password_bytes[:72]
                # 尝试解码，如果失败则逐步减少长度
                while len(password_bytes) > 0:
                    try:
                        password = password_bytes.decode('utf-8')
                        break
                    except UnicodeDecodeError:
                        password_bytes = password_bytes[:-1]
                if len(password_bytes) == 0:
                    password = "default"  # 如果完全无法解码，使用默认值
            
            return pwd_context.hash(password)
        except Exception as e:
            # 如果仍然失败，使用简单的哈希方法
            import hashlib
            return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """创建用户"""
        try:
            # 检查账号是否已存在
            existing_user = db.query(User).filter(User.account == user.account).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="账号已存在"
                )
            
            # 创建新用户
            hashed_password = UserService.get_password_hash(user.password)
            db_user = User(
                username=user.username,
                password=hashed_password,
                account=user.account,
                avatar_url=user.avatar_url
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号已存在"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建用户失败: {str(e)}"
            )
    
    @staticmethod
    def authenticate_user(db: Session, account: str, password: str) -> Optional[User]:
        """用户认证"""
        user = db.query(User).filter(User.account == account).first()
        if not user:
            return None
        if not UserService.verify_password(password, user.password):
            return None
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_account(db: Session, account: str) -> Optional[User]:
        """根据账号获取用户"""
        return db.query(User).filter(User.account == account).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100):
        """获取用户列表"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                return None
            
            update_data = user_update.dict(exclude_unset=True)
            
            # 如果更新密码，需要加密
            if "password" in update_data:
                update_data["password"] = UserService.get_password_hash(update_data["password"])
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            db.commit()
            db.refresh(db_user)
            return db_user
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新用户失败: {str(e)}"
            )
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户"""
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                return False
            
            db.delete(db_user)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除用户失败: {str(e)}"
            )
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            # 验证旧密码
            if not UserService.verify_password(old_password, db_user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="原密码错误"
                )
            
            # 更新密码
            db_user.password = UserService.get_password_hash(new_password)
            db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"修改密码失败: {str(e)}"
            )