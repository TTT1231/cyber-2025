"""

音转文

"""
from http import HTTPStatus
from dashscope.audio.asr import Transcription
import dashscope
import os
import json
import requests
# 若没有配置环境变量，请用百炼API Key将下行替换为：dashscope.api_key = "sk-xxx"




class Fun_ASR():
    @classmethod
    def transcribe(cls, audio_url):
        dashscope.api_key = os.getenv("API_KEY")
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
