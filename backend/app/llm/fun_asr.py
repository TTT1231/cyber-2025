"""

音转文

"""
from http import HTTPStatus
from dashscope.audio.asr import Transcription
import dashscope
import os
import json
import requests
from pathlib import Path




class Fun_ASR():
    @classmethod
    def _load_config(cls):
        """加载API配置"""
        config_path = Path(__file__).parent / "api_keys.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def transcribe(cls, audio_url):
        config = cls._load_config()
        dashscope.api_key = config["api_key"]
        task_response = Transcription.async_call(
            model='fun-asr',
            file_urls=[audio_url]
                        #['https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_female2.wav',
                        #'https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_male2.wav']
                        # 测试url
        )

        transcribe_response = Transcription.wait(task=task_response.output.task_id)
        if transcribe_response.status_code == HTTPStatus.OK:
            json_response = json.loads(json.dumps(transcribe_response.output, indent=4, ensure_ascii=False))
            transcription_url = json_response['results'][0]['transcription_url']
            return requests.get(transcription_url).json()['transcripts'][0]['text']
        else:
            print('ERROR:status_code: ', transcribe_response.status_code)
            return 0


Fun_ASR.transcribe("https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_female2.wav")
