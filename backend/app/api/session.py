from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.db.session import get_db
from app.api.user import get_current_user
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate, SessionResponse
from app.models.chat_sessions import ChatSessions
from app.models.chat_messages import ChatMessages

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

# POST /sessions - 创建新会话（绑定角色）
@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建新会话"""
    # 调用服务层创建会话
    db_session = SessionService.create_session(db, current_user.id, session)
    
    # 转换为响应模型
    return SessionResponse(
        id=db_session.id,
        role_id=db_session.role_id,
        last_message_at=db_session.last_message_at,
        created_at=db_session.created_at
    )

# GET /sessions - 获取会话列表
@router.get("/", response_model=List[SessionResponse])
def get_sessions(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    user_id: Optional[int] = Query(None, description="用户ID筛选（管理员功能）"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取会话列表，可按用户ID筛选"""
    # 如果指定了user_id且不是当前用户，需要管理员权限
    if user_id is not None and user_id != current_user.id:
        # 这里可以添加管理员权限检查
        # 暂时只允许用户查看自己的会话
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您只能查看自己的会话"
        )
    
    # 获取会话列表
    if user_id is None:
        # 默认获取当前用户的会话
        sessions = SessionService.get_sessions_by_user(db, current_user.id, skip, limit)
    else:
        sessions = SessionService.get_sessions_by_user(db, user_id, skip, limit)
    
    # 转换为响应模型
    return [
        SessionResponse(
            id=session.id,
            role_id=session.role_id,
            last_message_at=session.last_message_at,
            created_at=session.created_at
        )
        for session in sessions
    ]

# GET /sessions/{session_id} - 获取单个会话详情
@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个会话详情"""
    # 获取会话详情（只能获取自己的会话）
    session = SessionService.get_session_by_id(db, session_id, current_user.id)
    
    # 转换为响应模型
    return SessionResponse(
        id=session.id,
        role_id=session.role_id,
        last_message_at=session.last_message_at,
        created_at=session.created_at
    )

# DELETE /sessions/{session_id} - 删除会话
@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除会话"""
    # 删除会话（只能删除自己的会话）
    SessionService.delete_session(db, session_id, current_user.id)

# GET /sessions/role/{role_id} - 获取或创建用户与角色的会话
@router.get("/role/{role_id}", response_model=SessionResponse, summary="获取或创建用户与角色的会话")
def get_or_create_user_role_session(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取或创建用户与特定角色的会话
    - 如果用户与该角色已有会话，返回现有会话
    - 如果没有会话，创建新的会话
    - 每个用户与每个角色只能有一个会话
    """
    session = SessionService.get_or_create_user_role_session(
        db=db, 
        user_id=current_user.id, 
        role_id=role_id
    )
    
    return SessionResponse(
        id=session.id,
        role_id=session.role_id,
        last_message_at=session.last_message_at,
        created_at=session.created_at
    )

# GET /sessions/{session_id}/messages - 获取会话的消息列表（支持分页）
@router.get("/{session_id}/messages")
def get_session_messages(
    session_id: int,
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页消息数量，最大100"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取指定会话的消息列表（分页）
    
    特点：
    - 按时间倒序返回（最新消息在前）
    - 支持分页参数控制返回数量
    - 只能获取用户自己的会话消息
    """
    from app.services.message_service import MessageService
    return MessageService.get_messages_by_session(db, current_user.id, session_id, page, page_size)

@router.put("/{session_id}/update-time", status_code=status.HTTP_200_OK)
def update_session_time(
    session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新会话的最后消息时间"""
    # 首先验证会话是否属于当前用户
    SessionService.get_session_by_id(db, session_id, current_user.id)
    
    # 更新最后消息时间
    success = SessionService.update_last_message_time(db, session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新会话时间失败"
        )
    
    return {"message": "会话时间更新成功"}
