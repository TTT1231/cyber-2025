from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.session import SessionCreate, SessionResponse

router = APIRouter()

# POST /sessions - 创建新会话（绑定角色）
@router.post("/", response_model=SessionResponse)
def create_session(session: SessionCreate):
    """创建新会话"""
    # TODO: 实现创建会话逻辑
    pass

# GET /sessions - 获取会话列表
@router.get("/", response_model=List[SessionResponse])
def get_sessions(user_id: Optional[int] = Query(None, description="用户ID筛选")):
    """获取会话列表，可按用户ID筛选"""
    # TODO: 实现获取会话列表逻辑
    pass

# GET /sessions/{id} - 获取单个会话详情
@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int):
    """获取单个会话详情"""
    # TODO: 实现获取单个会话逻辑
    pass

# DELETE /sessions/{id} - 删除会话
@router.delete("/{session_id}")
def delete_session(session_id: int):
    """删除会话"""
    # TODO: 实现删除会话逻辑
    pass
