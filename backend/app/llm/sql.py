import pymysql
import pandas as pd
import json
from datetime import datetime

class CyberSQL(object):
    def __init__(self):
        self.DB_CONFIG = {
            'host': 'localhost',
            'database': 'cyber',
            'user': 'root',
            'password': '991211',
            'port': 3306,
            'charset': 'utf8mb4'
        }
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(**self.DB_CONFIG)
            print("数据库连接成功！")
        except pymysql.Error as e:
            print(f"数据库连接失败: {e}")

    def get_user_chat_history_json(self, user_id, limit=10):
        """获取特定用户的聊天历史，拼接成JSON格式，只取最近N个对话"""
        query = """
        SELECT 
            u.username,
            r.name as role_name,
            cs.id as session_id,
            cm.query_content,
            cm.answer_content,
            cm.message_type,
            cm.created_at
        FROM chat_sessions cs
        JOIN user u ON cs.user_id = u.id
        JOIN role r ON cs.role_id = r.id
        JOIN chat_messages cm ON cs.id = cm.session_id
        WHERE u.id = %s
        ORDER BY cm.created_at DESC
        LIMIT %s
        """

        df = pd.read_sql(query, self.connection, params=(user_id, limit))

        # 反转顺序，让最早的对话在前
        df = df.iloc[::-1].reset_index(drop=True)

        # 转换为JSON格式
        chat_history = {
            "user_id": user_id,
            "username": df.iloc[0]['username'] if len(df) > 0 else "Unknown",
            "total_messages": len(df),
            "latest_conversations": []
        }

        # 按会话分组处理
        sessions = {}
        for _, row in df.iterrows():
            session_id = row['session_id']
            if session_id not in sessions:
                sessions[session_id] = {
                    "session_id": session_id,
                    "role_name": row['role_name'],
                    "conversations": []
                }

            # 每个消息记录包含一问一答
            conversation = {
                "user_query": {
                    "content": row['query_content'],
                    "message_type": row['message_type'],
                    "created_at": row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(
                        row['created_at']) else None
                },
                "assistant_answer": {
                    "content": row['answer_content'],
                    "message_type": row['message_type'],
                    "created_at": row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(
                        row['created_at']) else None
                }
            }

            sessions[session_id]["conversations"].append(conversation)

        # 将会话添加到结果中
        for session in sessions.values():
            chat_history["latest_conversations"].append(session)
        #print(type(chat_history))
        #print(f"\n=== 用户ID {user_id} 的最近{limit}条对话记录(JSON格式) ===")
        #print(json.dumps(chat_history, ensure_ascii=False, indent=2))
        #print(type(chat_history))
        return chat_history

    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'connection'):
            self.connection.close()
            print("数据库连接已关闭")

# # 使用示例
# if __name__ == "__main__":
#     cyber_sql = CyberSQL()
#
#     try:
#         # 获取用户1的对话记录（按会话分组）
#         chat_history_grouped = cyber_sql.get_user_chat_history_json(user_id=1, limit=10)
#
#
#     finally:
#         cyber_sql.close()