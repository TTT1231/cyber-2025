from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.schemas.message import MessageCreate, MessageResponse, VoiceMessageRequest, VoiceMessageResponse
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

# POST /messages/voice - 处理语音对话
@router.post("/voice", response_model=VoiceMessageResponse)
async def process_voice_message(
    request: VoiceMessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    处理语音对话消息
    
    接收前端发送的语音转写文本，调用LLM生成回复，
    使用TTS生成语音文件，保存对话记录，返回音频URL
    
    请求格式：
    {
        "text": "用户说的话",
        "session_id": 1,
        "role_name": "哈利波特"
    }
    
    响应格式：
    {
        "audio_url": "https://...",
        "ai_text": "AI回复文本",
        "session_id": 1,
        "status": "success",
        "message": "语音对话处理成功"
    }
    """
    try:
        result = await MessageService.process_voice_message(
            db=db,
            user_id=current_user.id,
            session_id=request.session_id,
            user_text=request.text,
            role_name=request.role_name
        )
        
        return VoiceMessageResponse(
            audio_url=result["audio_url"],
            ai_text=result["ai_text"],
            session_id=result["session_id"],
            status=result["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音对话处理失败: {str(e)}"
        )
