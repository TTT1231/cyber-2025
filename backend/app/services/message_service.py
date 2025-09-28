from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio

from app.models.chat_messages import ChatMessages
from app.models.chat_sessions import ChatSessions
from app.schemas.message import MessageCreate, MessageResponse
from app.llm.llm_api import LLM
from app.llm.tts_api import TTS
from app.llm.prompt import Prompt

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
    
    @staticmethod
    def process_chat_message(db: Session, user_id: int, session_id: int, query: str, role_name: str = "哈利波特") -> Dict[str, Any]:
        """
        完整的聊天消息处理流程
        1. 保存用户消息
        2. 调用LLM生成回复
        3. 保存助手回复
        4. 调用TTS生成音频
        5. 返回完整结果
        """
        try:
            # 验证会话是否存在且用户有权限访问
            session = db.query(ChatSessions).filter(
                ChatSessions.id == session_id,
                ChatSessions.user_id == user_id
            ).first()
            
            if not session:
                logger.warning(f"用户 {user_id} 尝试在不存在或无权限的会话 {session_id} 中发送消息")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在或您没有权限访问"
                )
            
            # 1. 保存用户消息
            user_message_data = MessageCreate(
                session_id=session_id,
                role=1,  # 用户消息
                content=query,
                message_type="text",
                metadata={}
            )
            
            user_message = MessageService.create_message(db, user_id, user_message_data)
            logger.info(f"用户消息已保存: {user_message.id}")
            
            # 2. 获取历史消息用于上下文
            history_messages = MessageService._get_recent_messages(db, session_id, limit=10)
            
            # 3. 调用LLM生成回复
            system_prompt = MessageService._get_system_prompt_by_role(role_name)
            llm = LLM(role_name, system_prompt, max_turns=20)
            
            # 添加历史消息到LLM上下文
            MessageService._add_history_to_llm(llm, history_messages)
            
            # 生成LLM回复
            llm_response = llm.generate_output(query)
            logger.info(f"LLM回复已生成，长度: {len(llm_response)}")
            
            # 4. 调用TTS生成音频
            tts = TTS(voice="Cherry", language="Chinese")
            audio_url = tts.generate_audio(llm_response)
            logger.info(f"TTS音频已生成: {audio_url}")
            
            # 5. 保存助手回复（包含音频信息）
            assistant_message_data = MessageCreate(
                session_id=session_id,
                role=0,  # 助手消息
                content=llm_response,
                message_type="text",
                metadata={
                    "audio_url": audio_url,
                    "voice": "Cherry",
                    "language": "Chinese",
                    "role_name": role_name
                }
            )
            
            assistant_message = MessageService.create_message(db, user_id, assistant_message_data)
            logger.info(f"助手消息已保存: {assistant_message.id}")
            
            # 6. 返回完整结果
            return {
                "user_message": {
                    "id": user_message.id,
                    "content": user_message.content,
                    "created_at": user_message.created_at
                },
                "assistant_message": {
                    "id": assistant_message.id,
                    "content": assistant_message.content,
                    "audio_url": audio_url,
                    "created_at": assistant_message.created_at
                },
                "session_id": session_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"处理聊天消息时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="处理聊天消息失败"
            )
    
    @staticmethod
    def _get_recent_messages(db: Session, session_id: int, limit: int = 10) -> List[ChatMessages]:
        """获取最近的消息用于上下文"""
        return db.query(ChatMessages).filter(
            ChatMessages.session_id == session_id
        ).order_by(ChatMessages.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def _get_system_prompt_by_role(role_name: str) -> str:
        """根据角色名获取系统提示词"""
        role_prompts = {
            "哈利波特": Prompt.harry_potter,
            "哈姆雷特": Prompt.Hamlet,
            "苏格拉底": Prompt.Socrates
        }
        # 如果找不到对应的角色提示词，使用哈利波特作为默认值
        prompt = role_prompts.get(role_name, Prompt.harry_potter)
        logger.info(f"为角色 '{role_name}' 获取系统提示词，使用: {list(role_prompts.keys())[list(role_prompts.values()).index(prompt)] if prompt in role_prompts.values() else '默认(哈利波特)'}")
        return prompt
    
    @staticmethod
    def _add_history_to_llm(llm: LLM, history_messages: List[ChatMessages]):
        """将历史消息添加到LLM的上下文中"""
        # 按时间正序排列历史消息
        history_messages.reverse()
        
        for msg in history_messages:
            if msg.query_content:  # 用户消息
                llm.message.append({"role": "user", "content": msg.query_content})
            if msg.answer_content:  # 助手消息
                llm.message.append({"role": "assistant", "content": msg.answer_content})
    
    @staticmethod
    async def process_voice_message(db: Session, user_id: int, session_id: int, user_text: str, role_name: str = "哈利波特") -> Dict[str, Any]:
        """
        处理语音对话消息的异步方法
        1. 接收用户语音转写文本
        2. 调用LLM生成AI回复
        3. 使用TTS生成语音文件
        4. 保存对话记录到数据库
        5. 返回音频URL和AI文本
        """
        try:
            # 验证会话是否存在且用户有权限访问，同时获取角色信息
            session = db.query(ChatSessions).filter(
                ChatSessions.id == session_id,
                ChatSessions.user_id == user_id
            ).first()
            
            if not session:
                logger.warning(f"用户 {user_id} 尝试在不存在或无权限的会话 {session_id} 中发送语音消息")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话不存在或您没有权限访问"
                )
            
            # 从会话中获取角色信息
            from app.models.role import Role
            role = db.query(Role).filter(Role.id == session.role_id).first()
            if not role:
                logger.warning(f"会话 {session_id} 关联的角色 {session.role_id} 不存在")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="会话关联的角色不存在"
                )
            
            # 使用会话中的角色名称，而不是传入的参数
            actual_role_name = role.name
            logger.info(f"使用会话中的角色: {actual_role_name} (角色ID: {role.id})")
            
            # 获取历史消息用于上下文
            history_messages = MessageService._get_recent_messages(db, session_id, limit=10)
            
            # 初始化LLM并添加历史上下文，使用实际的角色名称
            system_prompt = MessageService._get_system_prompt_by_role(actual_role_name)
            llm = LLM(actual_role_name, system_prompt, max_turns=20)
            MessageService._add_history_to_llm(llm, history_messages)
            
            # 异步调用LLM生成回复
            ai_response = await asyncio.to_thread(llm.generate_output, user_text)
            logger.info(f"LLM异步生成回复完成，长度: {len(ai_response)}")
            
            # 异步调用TTS生成语音文件
            tts = TTS(voice="Cherry", language="Chinese")
            audio_url = await asyncio.to_thread(tts.generate_audio, ai_response)
            logger.info(f"TTS异步生成音频完成: {audio_url}")
            
            # 保存对话记录
            await MessageService._save_conversation(
                db=db,
                user_id=user_id,
                session_id=session_id,
                user_message=user_text,
                ai_message=ai_response,
                audio_url=audio_url,
                role_name=actual_role_name  # 使用实际的角色名称
            )
            
            return {
                "audio_url": audio_url,
                "ai_text": ai_response,
                "session_id": session_id,
                "status": "success"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"处理语音消息时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="处理语音消息失败"
            )
    
    @staticmethod
    async def _save_conversation(
        db: Session, 
        user_id: int, 
        session_id: int, 
        user_message: str, 
        ai_message: str, 
        audio_url: str,
        role_name: str
    ) -> Dict[str, int]:
        """
        异步保存对话记录到数据库
        """
        try:
            # 保存用户消息 (role=1)
            user_message_data = MessageCreate(
                session_id=session_id,
                role=1,  # 用户消息
                content=user_message,
                message_type="text",
                metadata={"source": "voice_input"}
            )
            
            user_msg = MessageService.create_message(db, user_id, user_message_data)
            logger.info(f"用户语音消息已保存: {user_msg.id}")
            
            # 保存助手消息 (role=0)
            assistant_message_data = MessageCreate(
                session_id=session_id,
                role=0,  # 助手消息
                content=ai_message,
                message_type="text",
                metadata={
                    "audio_url": audio_url,
                    "voice": "Cherry",
                    "language": "Chinese",
                    "role_name": role_name,
                    "source": "voice_output"
                }
            )
            
            assistant_msg = MessageService.create_message(db, user_id, assistant_message_data)
            logger.info(f"助手语音回复已保存: {assistant_msg.id}")
            
            return {
                "user_message_id": user_msg.id,
                "assistant_message_id": assistant_msg.id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存对话记录时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="保存对话记录失败"
            )