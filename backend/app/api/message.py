from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.message import MessageCreate, MessageResponse

router = APIRouter()

# POST /messages - 发送消息
@router.post("/", response_model=MessageResponse)
def create_message(message: MessageCreate):
    """发送消息（传 session_id、role=0/1、content、metadata）"""
    # TODO: 实现发送消息逻辑
    pass

# GET /messages - 获取某个会话的消息列表
@router.get("/", response_model=List[MessageResponse])
def get_messages(session_id: int = Query(..., description="会话ID")):
    """获取某个会话的消息列表"""
    # TODO: 实现获取消息列表逻辑
    pass
