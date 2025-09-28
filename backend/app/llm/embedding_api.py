import os
from openai import OpenAI
import json
from pathlib import Path

class Embedding():
    @classmethod
    def _load_config(cls):
        """加载API配置"""
        config_path = Path(__file__).parent / "api_keys.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def embedding(cls, text: str):
        config = cls._load_config()
        client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )

        completion = client.embeddings.create(
            model="text-embedding-v4",
            input=text
        )
        return json.loads(completion.model_dump_json())["data"][0]["embedding"]
