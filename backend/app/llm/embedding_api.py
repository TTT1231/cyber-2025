import os
from openai import OpenAI
import json





#print(completion.model_dump_json())

class Embedding():
    @classmethod
    def embedding(cls,text: str):
        client = OpenAI(
            # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
            # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
            api_key='sk-dcd129793262482cab9c357fb2d007fc',
            # 以下是北京地域base-url，如果使用新加坡地域的模型，需要将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼服务的base_url
        )

        completion = client.embeddings.create(
            model="text-embedding-v4",
            input=text
        )
        return json.loads(completion.model_dump_json())["data"][0]["embedding"]
#print(Embedding.embedding(input_texts))
