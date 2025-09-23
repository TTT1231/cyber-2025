import os
from openai import OpenAI
import json
class Embedding():
    @classmethod
    def embedding(cls, text: str):
        client = OpenAI(

            api_key=os.getenv("API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼服务的base_url
        )

        completion = client.embeddings.create(
            model="text-embedding-v4",
            input=text
        )
        return json.loads(completion.model_dump_json())["data"][0]["embedding"]
