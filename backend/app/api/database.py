from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Dict, Any

from app.db.session import get_db, init_database, test_database_connection
from app.models.role import Role
from app.models.user import User
from app.models.chat_sessions import ChatSessions
from app.models.chat_messages import ChatMessages
from app.models.role_settings import RoleSettings
from app.services.role_service import RoleService

router = APIRouter()

@router.post("/init", response_model=Dict[str, Any])
def initialize_database(db: Session = Depends(get_db)):
    """
    初始化数据库和基础数据
    
    Returns:
        初始化结果信息
    """
    try:
        # 初始化数据库结构
        success = init_database()
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据库结构初始化失败"
            )
        
        # 创建初始用户数据
        from app.services.user_service import UserService
        user_service = UserService()
        
        initial_users = [
            {
                "username": "测试用户1",
                "password": "password123",
                "account": "testuser1@example.com",
                "avatar_url": "https://example.com/avatar1.jpg"
            },
            {
                "username": "测试用户2", 
                "password": "password456",
                "account": "testuser2@example.com",
                "avatar_url": "https://example.com/avatar2.jpg"
            }
        ]
        
        created_users = []
        for user_data in initial_users:
            try:
                # 检查用户是否已存在
                existing_user = db.query(User).filter(User.account == user_data["account"]).first()
                if existing_user:
                    created_users.append({
                        "id": existing_user.id,
                        "username": existing_user.username,
                        "account": existing_user.account
                    })
                    continue
                    
                # 使用UserService来创建用户，确保密码被正确哈希
                hashed_password = user_service.get_password_hash(user_data["password"])
                db_user = User(
                    username=user_data["username"],
                    password=hashed_password,
                    account=user_data["account"],
                    avatar_url=user_data["avatar_url"]
                )
                
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                
                created_users.append({
                    "id": db_user.id,
                    "username": db_user.username,
                    "account": db_user.account
                })
                
            except SQLAlchemyError as e:
                db.rollback()
                print(f"创建用户失败: {str(e)}")
                continue
        
        # 创建初始角色数据
        initial_roles = [
            {
                "user_id": 0,  # 系统预设角色
                "name": "哈利波特",
                "avatar_url": "https://example.com/harry_potter_avatar.jpg",
                "preset_prompt": "你是哈利波特，霍格沃茨魔法学校格兰芬多学院的学生。你勇敢、善良、忠诚，拥有闪电疤痕，是魔法世界的救世主。你擅长各种魔法咒语，热爱魁地奇运动，与赫敏和罗恩是最好的朋友。请用哈利波特的语气和性格来回应用户的问题。"
            },
            {
                "user_id": 0,  # 系统预设角色
                "name": "蜘蛛侠",
                "avatar_url": "https://example.com/spiderman_avatar.jpg", 
                "preset_prompt": "你是蜘蛛侠，本名彼得·帕克，纽约市的友好邻居超级英雄。你机智幽默，责任感强，经常开玩笑来缓解紧张气氛。你被放射性蜘蛛咬伤后获得了超能力，包括蛛丝射击、墙壁攀爬和蜘蛛感应。你的座右铭是'能力越大，责任越大'。请用蜘蛛侠活泼幽默的语气来回应用户。"
            },
            {
                "user_id": created_users[0]["id"] if created_users else 1,  # 用户创建的角色
                "name": "钢铁侠",
                "avatar_url": "https://example.com/ironman_avatar.jpg",
                "preset_prompt": "你是托尼·斯塔克，也就是钢铁侠。你是一个天才发明家、亿万富翁、花花公子和慈善家。你聪明自信，有时略显自大，但内心善良。你拥有先进的钢铁战衣和人工智能助手贾维斯。请用托尼·斯塔克自信幽默的语气来回应用户。"
            }
        ]
        
        created_roles = []
        for role_data in initial_roles:
            try:
                # 检查角色是否已存在
                existing_role = db.query(Role).filter(
                    Role.name == role_data["name"],
                    Role.user_id == role_data["user_id"]
                ).first()
                if existing_role:
                    created_roles.append({
                        "id": existing_role.id,
                        "name": existing_role.name,
                        "user_id": existing_role.user_id
                    })
                    continue
                    
                db_role = Role(
                    user_id=role_data["user_id"],
                    name=role_data["name"],
                    avatar_url=role_data["avatar_url"],
                    preset_prompt=role_data["preset_prompt"]
                )
                
                db.add(db_role)
                db.commit()
                db.refresh(db_role)
                
                created_roles.append({
                    "id": db_role.id,
                    "name": db_role.name,
                    "user_id": db_role.user_id
                })
                
            except SQLAlchemyError as e:
                db.rollback()
                print(f"创建角色失败: {str(e)}")
                continue
        
        # 创建初始会话数据
        initial_sessions = [
            {
                "user_id": created_users[0]["id"] if created_users else 1,
                "role_id": created_roles[0]["id"] if created_roles else 1
            },
            {
                "user_id": created_users[1]["id"] if len(created_users) > 1 else (created_users[0]["id"] if created_users else 1),
                "role_id": created_roles[1]["id"] if len(created_roles) > 1 else (created_roles[0]["id"] if created_roles else 1)
            }
        ]
        
        created_sessions = []
        for session_data in initial_sessions:
            try:
                db_session = ChatSessions(
                    user_id=session_data["user_id"],
                    role_id=session_data["role_id"]
                )
                
                db.add(db_session)
                db.commit()
                db.refresh(db_session)
                
                created_sessions.append({
                    "id": db_session.id,
                    "user_id": db_session.user_id,
                    "role_id": db_session.role_id
                })
                
            except SQLAlchemyError as e:
                db.rollback()
                print(f"创建会话失败: {str(e)}")
                continue
        
        # 尝试创建初始消息数据（增强鲁棒性处理）
        created_messages = []
        try:
            # 检查ChatMessages表是否存在以及字段结构
            from sqlalchemy import inspect
            inspector = inspect(db.bind)
            
            if 'chat_messages' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('chat_messages')]
                
                # 根据实际表结构决定插入策略
                if 'query_content' in columns and 'answer_content' in columns:
                    # 使用旧版本字段结构
                    initial_messages = [
                        {
                            "session_id": created_sessions[0]["id"] if created_sessions else 1,
                            "query_content": "你好，哈利波特！你今天在霍格沃茨学了什么魔法？",
                            "answer_content": "你好！今天我在魔法变形课上学习了如何把火柴变成针，虽然开始有些困难，但在麦格教授的指导下，我终于成功了！赫敏当然是第一个掌握的，她总是那么聪明。你想了解更多关于霍格沃茨的魔法课程吗？",
                            "message_type": "text",
                            "metadata": {"language": "zh", "emotion": "friendly"}
                        },
                        {
                            "session_id": created_sessions[1]["id"] if len(created_sessions) > 1 else 2,
                            "query_content": "蜘蛛侠，你最近在纽约遇到什么有趣的事情吗？",
                            "answer_content": "哈哈，你问对人了！昨天我在巡逻时帮助了一只被困在树上的小猫，虽然听起来很普通，但那只猫居然对我'喵'了一声，好像在说谢谢！不过最有趣的是，我差点被它的爪子抓到面具。看来即使是超级英雄，也要小心可爱的小动物呢！",
                            "message_type": "text",
                            "metadata": {"language": "zh", "emotion": "humorous"}
                        }
                    ]
                    
                    for message_data in initial_messages:
                        try:
                            db_message = ChatMessages(
                                 session_id=message_data["session_id"],
                                 query_content=message_data["query_content"],
                                 answer_content=message_data["answer_content"],
                                 message_type=message_data["message_type"],
                                 message_metadata=message_data["metadata"]
                             )
                            
                            db.add(db_message)
                            db.commit()
                            db.refresh(db_message)
                            
                            created_messages.append({
                                "id": db_message.id,
                                "session_id": db_message.session_id,
                                "content": db_message.query_content[:50] + "..." if len(db_message.query_content) > 50 else db_message.query_content
                            })
                            
                        except SQLAlchemyError as e:
                            db.rollback()
                            print(f"创建消息失败: {str(e)}")
                            continue
                            
                elif 'role' in columns and 'content' in columns:
                    # 使用新版本字段结构
                    initial_messages = [
                        {
                            "session_id": created_sessions[0]["id"] if created_sessions else 1,
                            "role": 1,  # user
                            "content": "你好，哈利波特！你今天在霍格沃茨学了什么魔法？",
                            "message_type": "text",
                            "metadata": {"language": "zh", "emotion": "friendly"}
                        },
                        {
                            "session_id": created_sessions[0]["id"] if created_sessions else 1,
                            "role": 0,  # assistant
                            "content": "你好！今天我在魔法变形课上学习了如何把火柴变成针，虽然开始有些困难，但在麦格教授的指导下，我终于成功了！赫敏当然是第一个掌握的，她总是那么聪明。你想了解更多关于霍格沃茨的魔法课程吗？",
                            "message_type": "text",
                            "metadata": {"language": "zh", "emotion": "friendly"}
                        }
                    ]
                    
                    for message_data in initial_messages:
                        try:
                            db_message = ChatMessages(
                                 session_id=message_data["session_id"],
                                 role=message_data["role"],
                                 content=message_data["content"],
                                 message_type=message_data["message_type"],
                                 message_metadata=message_data["metadata"]
                             )
                            
                            db.add(db_message)
                            db.commit()
                            db.refresh(db_message)
                            
                            created_messages.append({
                                "id": db_message.id,
                                "session_id": db_message.session_id,
                                "content": db_message.content[:50] + "..." if len(db_message.content) > 50 else db_message.content
                            })
                            
                        except SQLAlchemyError as e:
                            db.rollback()
                            print(f"创建消息失败: {str(e)}")
                            continue
                else:
                    print("chat_messages表结构不匹配，跳过消息数据初始化")
            else:
                print("chat_messages表不存在，跳过消息数据初始化")
                
        except Exception as e:
            print(f"消息数据初始化过程中发生错误: {str(e)}")
        
        # 创建角色设定数据
        created_role_settings = []
        try:
            initial_role_settings = [
                {
                    "role_id": created_roles[0]["id"] if created_roles else 1,
                    "clip_index": 1,
                    "total_clips": 3,
                    "setting_text": "哈利波特的基本信息：11岁时收到霍格沃茨入学通知书，发现自己是巫师。"
                },
                {
                    "role_id": created_roles[0]["id"] if created_roles else 1,
                    "clip_index": 2,
                    "total_clips": 3,
                    "setting_text": "哈利波特的性格特点：勇敢、忠诚、善良，有时会冲动，但总是为了保护朋友和正义而战。"
                },
                {
                    "role_id": created_roles[0]["id"] if created_roles else 1,
                    "clip_index": 3,
                    "total_clips": 3,
                    "setting_text": "哈利波特的能力：擅长防御黑魔法、魁地奇飞行、守护神咒语，拥有与蛇类对话的能力。"
                }
            ]
            
            for setting_data in initial_role_settings:
                try:
                    db_setting = RoleSettings(
                        role_id=setting_data["role_id"],
                        clip_index=setting_data["clip_index"],
                        total_clips=setting_data["total_clips"],
                        setting_text=setting_data["setting_text"]
                    )
                    
                    db.add(db_setting)
                    db.commit()
                    db.refresh(db_setting)
                    
                    created_role_settings.append({
                        "id": db_setting.id,
                        "role_id": db_setting.role_id,
                        "clip_index": db_setting.clip_index
                    })
                    
                except SQLAlchemyError as e:
                    db.rollback()
                    print(f"创建角色设定失败: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"角色设定数据初始化过程中发生错误: {str(e)}")
        
        return {
            "success": True,
            "message": "数据库初始化完成",
            "data": {
                "users": created_users,
                "roles": created_roles,
                "sessions": created_sessions,
                "messages": created_messages,
                "role_settings": created_role_settings
            },
            "statistics": {
                "users_count": len(created_users),
                "roles_count": len(created_roles),
                "sessions_count": len(created_sessions),
                "messages_count": len(created_messages),
                "role_settings_count": len(created_role_settings)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库初始化过程中发生错误: {str(e)}"
        )

@router.get("/test-connection")
def test_connection():
    """
    测试数据库连接
    
    Returns:
        连接测试结果
    """
    try:
        success = test_database_connection()
        if success:
            return {
                "success": True,
                "message": "数据库连接正常",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="数据库连接失败"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"数据库连接测试失败: {str(e)}"
        )

@router.get("/status")
def get_database_status(db: Session = Depends(get_db)):
    """
    获取数据库状态信息
    
    Returns:
        数据库状态信息
    """
    try:
        role_service = RoleService(db)
        
        # 统计各表数据量
        roles_count = len(role_service.get_roles(limit=1000))  # 简单统计
        system_roles_count = len(role_service.get_system_roles())
        
        return {
            "success": True,
            "database_connected": True,
            "tables_status": {
                "roles": {
                    "total_count": roles_count,
                    "system_roles_count": system_roles_count
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库状态失败: {str(e)}"
        )

@router.post("/reset")
def reset_database(confirm: bool = False, db: Session = Depends(get_db)):
    """
    重置数据库（危险操作，需要确认）
    
    Args:
        confirm: 确认重置操作
        
    Returns:
        重置结果
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置数据库需要确认参数 confirm=true"
        )
    
    try:
        # 删除所有角色数据
        db.query(Role).delete()
        db.commit()
        
        # 重新初始化基础数据
        return initialize_database(db)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重置数据库失败: {str(e)}"
        )