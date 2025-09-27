from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.models.chat_messages import ChatMessages
from app.models.chat_sessions import ChatSessions
from app.schemas.message import MessageCreate, MessageResponse

# 配置日志
logger = logging.getLogger(__name__)

class MessageService:
    """消息服务类"""
    
    @staticmethod
    def create_message(db: Session, user_id: int, message_data: MessageCreate) -> MessageResponse:
        """创建新消息"""
        try:
            # 验证会话是否存在且用户有权限访问
            session = db.query(ChatSessions).filter(
                ChatSessions.id == message_data.session_id,
                ChatSessions.user_id == user_id
            ).first()
            
            if not session:
                logger.warning(f"用户 {user_id} 尝试在不存在或无权限的会话 {message_data.session_id} 中创建消息")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在或您没有权限访问"
                )
            
            # 根据角色创建消息
            if message_data.role == 1:  # 用户消息
                db_message = ChatMessages(
                    session_id=message_data.session_id,
                    query_content=message_data.content,
                    answer_content="",  # 用户消息时答案为空
                    message_type=message_data.message_type,
                    message_metadata=message_data.metadata or {}
                )
            else:  # 助手消息 (role == 0)
                db_message = ChatMessages(
                    session_id=message_data.session_id,
                    query_content="",  # 助手消息时问题为空
                    answer_content=message_data.content,
                    message_type=message_data.message_type,
                    message_metadata=message_data.metadata or {}
                )
            
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            
            # 更新会话的最后消息时间
            session.last_message_at = db_message.created_at
            db.commit()
            
            logger.info(f"用户 {user_id} 在会话 {message_data.session_id} 中成功创建消息 {db_message.id}")
            
            return MessageResponse(
                id=db_message.id,
                session_id=db_message.session_id,
                role=message_data.role,
                content=message_data.content,
                message_type=db_message.message_type,
                metadata=db_message.message_metadata,
                created_at=db_message.created_at
            )
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"创建消息时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建消息失败"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"创建消息时未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建消息失败"
            )
    
    @staticmethod
    def get_messages_by_session(
        db: Session, 
        user_id: int, 
        session_id: int, 
        page: int = 1, 
        page_size: int = 50
    ) -> Dict[str, Any]:
        """获取会话的消息列表（分页）"""
        try:
            # 验证会话是否存在且用户有权限访问
            session = db.query(ChatSessions).filter(
                ChatSessions.id == session_id,
                ChatSessions.user_id == user_id
            ).first()
            
            if not session:
                logger.warning(f"用户 {user_id} 尝试访问不存在或无权限的会话 {session_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在或您没有权限访问"
                )
            
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 获取消息总数
            total_count = db.query(ChatMessages).filter(
                ChatMessages.session_id == session_id
            ).count()
            
            # 获取分页消息（按时间倒序，最新的在前）
            messages = db.query(ChatMessages).filter(
                ChatMessages.session_id == session_id
            ).order_by(ChatMessages.created_at.desc()).offset(offset).limit(page_size).all()
            
            # 转换为响应格式
            message_responses = []
            for msg in messages:
                # 根据内容判断角色和获取内容
                if msg.query_content:
                    role = 1  # 用户消息
                    content = msg.query_content
                else:
                    role = 0  # 助手消息
                    content = msg.answer_content
                
                message_responses.append(MessageResponse(
                    id=msg.id,
                    session_id=msg.session_id,
                    role=role,
                    content=content,
                    message_type=msg.message_type,
                    metadata=msg.message_metadata or {},
                    created_at=msg.created_at
                ))
            
            # 计算分页信息
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_prev = page > 1
            
            logger.info(f"用户 {user_id} 获取会话 {session_id} 的消息列表，页码 {page}，共 {len(message_responses)} 条")
            
            return {
                "messages": message_responses,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": has_next,
                    "has_prev": has_prev
                }
            }
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"获取消息列表时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取消息列表失败"
            )
        except Exception as e:
            logger.error(f"获取消息列表时未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取消息列表失败"
            )
    
    @staticmethod
    def get_message_by_id(db: Session, user_id: int, message_id: int) -> MessageResponse:
        """根据ID获取消息详情"""
        try:
            # 通过消息ID和用户权限查询消息
            message = db.query(ChatMessages).join(ChatSessions).filter(
                ChatMessages.id == message_id,
                ChatSessions.user_id == user_id
            ).first()
            
            if not message:
                logger.warning(f"用户 {user_id} 尝试访问不存在或无权限的消息 {message_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="消息不存在或您没有权限访问"
                )
            
            # 根据内容判断角色和获取内容
            if message.query_content:
                role = 1  # 用户消息
                content = message.query_content
            else:
                role = 0  # 助手消息
                content = message.answer_content
            
            logger.info(f"用户 {user_id} 成功获取消息 {message_id}")
            
            return MessageResponse(
                id=message.id,
                session_id=message.session_id,
                role=role,
                content=content,
                message_type=message.message_type,
                metadata=message.message_metadata or {},
                created_at=message.created_at
            )
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"获取消息详情时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取消息详情失败"
            )
        except Exception as e:
            logger.error(f"获取消息详情时未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取消息详情失败"
            )
    
    @staticmethod
    def delete_message(db: Session, user_id: int, message_id: int) -> bool:
        """删除消息"""
        try:
            # 通过消息ID和用户权限查询消息
            message = db.query(ChatMessages).join(ChatSessions).filter(
                ChatMessages.id == message_id,
                ChatSessions.user_id == user_id
            ).first()
            
            if not message:
                logger.warning(f"用户 {user_id} 尝试删除不存在或无权限的消息 {message_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="消息不存在或您没有权限删除"
                )
            
            db.delete(message)
            db.commit()
            
            logger.info(f"用户 {user_id} 成功删除消息 {message_id}")
            return True
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"删除消息时数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除消息失败"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"删除消息时未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除消息失败"
            )