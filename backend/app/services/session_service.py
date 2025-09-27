from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import logging

from app.models.chat_sessions import ChatSessions
from app.models.role import Role
from app.schemas.session import SessionCreate

# 配置日志
logger = logging.getLogger(__name__)

class SessionService:
    """会话服务类"""
    
    @staticmethod
    def create_session(db: Session, user_id: int, session_data: SessionCreate) -> ChatSessions:
        """创建新会话"""
        try:
            # 验证角色是否存在
            role = db.query(Role).filter(Role.id == session_data.role_id).first()
            if not role:
                logger.warning(f"尝试创建会话时角色不存在: role_id={session_data.role_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定的角色不存在"
                )
            
            # 检查用户是否有权限使用该角色
            if role.user_id != 0 and role.user_id != user_id:
                logger.warning(f"用户 {user_id} 尝试使用无权限的角色 {session_data.role_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您没有权限使用该角色"
                )
            
            # 创建新会话
            db_session = ChatSessions(
                user_id=user_id,
                role_id=session_data.role_id,
                created_at=datetime.now()
            )
            
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            logger.info(f"用户 {user_id} 成功创建会话 {db_session.id}，角色 {session_data.role_id}")
            return db_session
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"创建会话时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建会话失败"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"创建会话时未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建会话失败"
            )
    
    @staticmethod
    def get_sessions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatSessions]:
        """获取用户的会话列表"""
        try:
            sessions = db.query(ChatSessions).filter(
                ChatSessions.user_id == user_id
            ).order_by(ChatSessions.created_at.desc()).offset(skip).limit(limit).all()
            
            logger.info(f"获取用户 {user_id} 的会话列表，共 {len(sessions)} 个会话")
            return sessions
            
        except SQLAlchemyError as e:
            logger.error(f"获取用户会话列表时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取会话列表失败"
            )
    
    @staticmethod
    def get_all_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[ChatSessions]:
        """获取所有会话列表（管理员功能）"""
        try:
            sessions = db.query(ChatSessions).order_by(
                ChatSessions.created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.info(f"获取所有会话列表，共 {len(sessions)} 个会话")
            return sessions
            
        except SQLAlchemyError as e:
            logger.error(f"获取所有会话列表时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取会话列表失败"
            )
    
    @staticmethod
    def get_session_by_id(db: Session, session_id: int, user_id: Optional[int] = None) -> ChatSessions:
        """根据ID获取会话详情"""
        try:
            query = db.query(ChatSessions).filter(ChatSessions.id == session_id)
            
            # 如果指定了用户ID，则只能获取该用户的会话
            if user_id is not None:
                query = query.filter(ChatSessions.user_id == user_id)
            
            session = query.first()
            
            if not session:
                logger.warning(f"会话不存在或无权限访问: session_id={session_id}, user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在或您没有权限访问"
                )
            
            logger.info(f"成功获取会话详情: session_id={session_id}")
            return session
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"获取会话详情时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取会话详情失败"
            )
    
    @staticmethod
    def delete_session(db: Session, session_id: int, user_id: Optional[int] = None) -> bool:
        """删除会话"""
        try:
            query = db.query(ChatSessions).filter(ChatSessions.id == session_id)
            
            # 如果指定了用户ID，则只能删除该用户的会话
            if user_id is not None:
                query = query.filter(ChatSessions.user_id == user_id)
            
            session = query.first()
            
            if not session:
                logger.warning(f"尝试删除不存在的会话或无权限: session_id={session_id}, user_id={user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在或您没有权限删除"
                )
            
            db.delete(session)
            db.commit()
            
            logger.info(f"成功删除会话: session_id={session_id}, user_id={user_id}")
            return True
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"删除会话时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除会话失败"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"删除会话时未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除会话失败"
            )
    
    @staticmethod
    def get_or_create_user_role_session(db: Session, user_id: int, role_id: int) -> ChatSessions:
        """获取或创建用户与特定角色的会话（每个用户与每个角色只有一个会话）"""
        try:
            # 首先验证角色是否存在
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                logger.warning(f"尝试获取会话时角色不存在: role_id={role_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定的角色不存在"
                )
            
            # 检查用户是否有权限使用该角色（系统角色user_id=0，或者是用户自己创建的角色）
            if role.user_id != 0 and role.user_id != user_id:
                logger.warning(f"用户 {user_id} 尝试使用无权限的角色 {role_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您没有权限使用该角色"
                )
            
            # 查找是否已存在该用户与该角色的会话
            existing_session = db.query(ChatSessions).filter(
                ChatSessions.user_id == user_id,
                ChatSessions.role_id == role_id
            ).first()
            
            if existing_session:
                logger.info(f"找到用户 {user_id} 与角色 {role_id} 的现有会话: {existing_session.id}")
                return existing_session
            
            # 如果不存在，创建新会话
            new_session = ChatSessions(
                user_id=user_id,
                role_id=role_id,
                created_at=datetime.now()
            )
            
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            logger.info(f"为用户 {user_id} 与角色 {role_id} 创建新会话: {new_session.id}")
            return new_session
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"获取或创建用户角色会话时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取或创建会话失败"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"获取或创建用户角色会话时未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取或创建会话失败"
            )
    
    @staticmethod
    def update_last_message_time(db: Session, session_id: int, message_time: Optional[datetime] = None) -> bool:
        """更新会话的最后消息时间"""
        try:
            session = db.query(ChatSessions).filter(ChatSessions.id == session_id).first()
            
            if not session:
                logger.warning(f"尝试更新不存在的会话时间: session_id={session_id}")
                return False
            
            session.last_message_at = message_time or datetime.now()
            db.commit()
            
            logger.info(f"成功更新会话最后消息时间: session_id={session_id}")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"更新会话最后消息时间时数据库错误: {str(e)}")
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"更新会话最后消息时间时未知错误: {str(e)}")
            return False