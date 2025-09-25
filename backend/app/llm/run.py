from prompt import Prompt
from rag import Rag
from tts_api import TTS
from llm_api import LLM
from fun_asr import Fun_ASR
from config import Config

class Run(object):
    def __init__(self):
        """
        初始化相关参数
        """
        self.config = Config()
