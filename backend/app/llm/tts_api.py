#  DashScope SDK 版本不低于 1.24.6
import os
import dashscope
import json
from pathlib import Path

class TTS():
    def __init__(self, voice: str, language: str):
        self.voice = voice
        self.language = language
    
    def _load_config(self):
        """加载API配置"""
        config_path = Path(__file__).parent / "api_keys.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_audio(self,text:str):
        config = self._load_config()
        response = dashscope.MultiModalConversation.call(
            model="qwen3-tts-flash",
            api_key=config["api_key"],
            text=text,
            voice="Cherry",
            language_type="Chinese",  # 建议与文本语种一致，以获得正确的发音和自然的语调。
            stream=False
        )

        # 添加错误检查
        if response is None:
            raise Exception("TTS API返回None响应")
        
        if not hasattr(response, 'output') or response.output is None:
            raise Exception(f"TTS API响应格式错误: {response}")
            
        if not hasattr(response.output, 'audio') or response.output.audio is None:
            raise Exception(f"TTS API未返回音频数据: {response.output}")

        return response.output.audio.url    # 返回音频url

# 测试代码已移除，避免在导入时执行
# if __name__ == "__main__":
#     tts = TTS('Cherry','Chinese')
#     print(tts.generate_audio('你好，我是哈利波特'))



