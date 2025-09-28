"""
测试语音对话中角色获取功能
验证系统是否能正确从会话中获取角色信息
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.services.message_service import MessageService
from app.models.chat_sessions import ChatSessions
from app.models.role import Role
from app.models.chat_messages import ChatMessages
from app.db.session import Base

# 创建测试数据库
engine = create_engine("sqlite:///test_role_voice.db", echo=False)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def test_role_voice_conversation():
    """测试角色语音对话功能"""
    db = SessionLocal()
    
    try:
        print("🧪 开始测试角色语音对话功能...")
        
        # 1. 创建测试角色
        test_role = Role(
            id=1,
            user_id=0,  # 系统角色
            name="哈姆雷特",
            avatar_url="https://example.com/hamlet.jpg",
            preset_prompt="我是哈姆雷特，丹麦王子..."
        )
        db.add(test_role)
        db.commit()
        print(f"✅ 创建测试角色: {test_role.name} (ID: {test_role.id})")
        
        # 2. 创建测试会话，关联到哈姆雷特角色
        test_session = ChatSessions(
            id=1,
            user_id=1,
            role_id=1  # 关联到哈姆雷特角色
        )
        db.add(test_session)
        db.commit()
        print(f"✅ 创建测试会话: ID={test_session.id}, 关联角色ID={test_session.role_id}")
        
        # 3. 测试语音对话处理
        print("\n🎭 测试语音对话处理...")
        user_text = "你好，请介绍一下你自己"
        
        # 注意：这里传入的role_name应该被忽略，系统应该使用会话中的角色
        result = await MessageService.process_voice_message(
            db=db,
            user_id=1,
            session_id=1,
            user_text=user_text,
            role_name="哈利波特"  # 这个应该被忽略
        )
        
        print(f"✅ 语音对话处理成功!")
        print(f"   音频URL: {result['audio_url']}")
        print(f"   AI回复: {result['ai_text'][:100]}...")
        print(f"   会话ID: {result['session_id']}")
        print(f"   状态: {result['status']}")
        
        # 4. 验证保存的消息记录
        messages = db.query(ChatMessages).filter(ChatMessages.session_id == 1).all()
        print(f"\n📝 验证保存的消息记录 (共{len(messages)}条):")
        
        for msg in messages:
            if msg.query_content:
                print(f"   用户消息: {msg.query_content}")
                print(f"   元数据: {msg.message_metadata}")
            if msg.answer_content:
                print(f"   AI回复: {msg.answer_content[:50]}...")
                print(f"   元数据: {msg.message_metadata}")
        
        print("\n🎉 角色语音对话功能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

# if __name__ == "__main__":
#     asyncio.run(test_role_voice_conversation())