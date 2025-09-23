import os
from dashscope import Generation
import dashscope
from prompt import Prompt

class LLM():
    def __init__(self, role_name: str, system_prompt: str, max_turns: int):

        """
        :param role_name: 角色名
        :param system_prompt: 系统提示词
        :param max_turns: 最大对话轮数
        """
        self.llm_name = 'qwen-flash'
        self.role_name = role_name
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        """
        配置用户变量：API_KEY your api key 
        重启IDE
        """
        self.message = [{"role": "system", "content": self.system_prompt}]

    def update_max_turns(self,max_turns):
        """
        支持修改最大对话轮数
        """
        self.max_turns = max_turns

    def update_system_prompt(self,system_prompt):
        """
        支持修改system prompt
        """
        self.system_prompt = system_prompt

    def generate_output(self, query):
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1/"
        self.update_chat_memory({"role": "user", "content": query})
        answer_content = ''
        completion = Generation.call(
            # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key = "sk-xxx",
            api_key=os.getenv("API_KEY"),
            # api_key="sk-dcd129793262482cab9c357fb2d007fc",
            # 可按需更换为其它深度思考模型
            model="qwen-flash",
            messages=self.message,
            result_format="message",  # Qwen3开源版模型只支持设定为"message"；为了更好的体验，其它模型也推荐您优先设定为"message"
            enable_thinking=False,
            stream=True,
            incremental_output=True,  # Qwen3开源版模型只支持 true；为了更好的体验，其它模型也推荐您优先设定为 true

        )
        for chunk in completion:
            #print(chunk)
            if chunk["status_code"]!=200:
                error_msg = f"API调用失败！状态码: {chunk.get('status_code')}, 错误信息: {chunk.get('message', '未知错误')}"
                raise Exception(error_msg)
            answer_content += chunk.output.choices[0].message.content
        self.update_chat_memory({"role": "assistant", "content": answer_content})
        return answer_content

    def update_chat_memory(self,message):
        self.message.append(message)
        if len(self.message) > self.max_turns:
            self.message.reverse()
            self.message.pop(-2)
            self.message.pop(-2)
            self.message.reverse()
llm = LLM("哈利波特",Prompt.harry_potter,20)
while True:
    querys = input("")
    print(llm.generate_output(querys))
    #print('---------------------------------')
    #print(llm.message)

