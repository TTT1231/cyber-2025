#  DashScope SDK 版本不低于 1.24.6
import os
import dashscope

class TTS():
    def __init__(self, voice: str, language: str):
        self.voice = voice
        self.language = language
    def generate_audio(self,text:str):
        response = dashscope.MultiModalConversation.call(
            model="qwen3-tts-flash",
            api_key=os.getenv("API_KEY"),
            text=text,
            voice="Cherry",
            language_type="Chinese",  # 建议与文本语种一致，以获得正确的发音和自然的语调。
            stream=False
        )

        return response.output.audio.url    # 返回音频url


tts = TTS('Cherry','Chinese')
print(tts.generate_audio('你好，我是哈利波特'))



