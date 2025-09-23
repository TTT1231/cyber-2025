import numpy as np
from sql import CyberSQL
from embedding_api import Embedding


class Rag():
    def __init__(self, user_id, role_name):
        self.cybersql = CyberSQL()  # 初始化数据库
        self.user_id = user_id      # user_id
        self.role_name = role_name

    def get_content(self, query: str) -> str:
        try:
            from numpy.linalg import norm

            # 获取查询的嵌入向量
            query_vector = np.array(Embedding.embedding(query)).flatten()

            # 获取历史查询
            history_query = self.get_history_query()
            if not history_query:
                return " "

            # 计算相似度（使用余弦相似度）
            similarity = []
            for hv in history_query:
                history_vector = np.array(Embedding.embedding(hv)).flatten()

                # 计算余弦相似度
                if norm(query_vector) > 0 and norm(history_vector) > 0:
                    cos_sim = np.dot(query_vector, history_vector) / (norm(query_vector) * norm(history_vector))
                else:
                    cos_sim = 0

                similarity.append(cos_sim)

            # 找到最相似的历史查询
            max_similarity_index = np.argmax(similarity)
            max_similarity_value = similarity[max_similarity_index]

            print(f"最大余弦相似度: {max_similarity_value:.4f}")

            # 设置相似度阈值，避免返回不相关的结果
            if max_similarity_value < 0.4:  # 调整阈值
                print("未找到足够相似的历史对话")
                return " "

            # 获取对应的答案
            history_answer = self.get_history_answer()
            return history_answer[int(max_similarity_index)]

        except Exception as e:
            print(f"获取内容时出错: {e}")
            return " "

    def get_history_query(self):

        history_chat = self.cybersql.get_user_chat_history_json(self.user_id, limit=100)  # 获取历史对话数据
        latest_conversations = history_chat["latest_conversations"]
        history_query = []
        for talks in latest_conversations:
            for conversations in talks['conversations']:
                history_query.append(conversations["user_query"]["content"])

        return history_query

    def get_history_answer(self):
        try:
            history_chat = self.cybersql.get_user_chat_history_json(self.user_id, limit=100)  # 获取历史对话数据

            latest_conversations = history_chat["latest_conversations"]
            history_query = []
            for talks in latest_conversations:
                for conversations in talks['conversations']:
                    history_query.append(conversations["assistant_answer"]["content"])
        finally:
            self.cybersql.close()
        return history_query

    def generate_output(self,query):
        memory = self.get_content(query)



