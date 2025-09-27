from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.schemas.message import MessageCreate, MessageResponse
from app.services.message_service import MessageService
from app.db.session import get_db
from app.api.user import get_current_user

router = APIRouter()

# POST /messages - 发送消息
@router.post("/", response_model=MessageResponse)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """发送消息（传 session_id、role=0/1、content、metadata）"""
    return MessageService.create_message(db, current_user.id, message)

# GET /messages - 获取某个会话的消息列表
@router.get("/", response_model=List[MessageResponse])
def get_messages(
    session_id: int = Query(..., description="会话ID"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取某个会话的消息列表"""
    result = MessageService.get_messages_by_session(db, current_user.id, session_id)
    return result["messages"]

# GET /messages/{message_id} - 获取单个消息详情
@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个消息详情"""
    return MessageService.get_message_by_id(db, current_user.id, message_id)

# DELETE /messages/{message_id} - 删除消息
@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除消息"""
    success = MessageService.delete_message(db, current_user.id, message_id)
    if success:
        return {"message": "消息删除成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除消息失败"
        )
