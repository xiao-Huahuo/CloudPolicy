import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
# 环境变量现在由 main.py 统一加载，此处仅在单独测试时加载
# load_dotenv()

class RequestKimi:
    def __init__(self):
        self.api_key = os.getenv("MOONSHOT_API_KEY")
        if not self.api_key:
            raise ValueError("MOONSHOT_API_KEY is not set in environment variables (check .env file)")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.moonshot.cn/v1",
        )
        self.system_prompt = "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"

    def get_response(self, content: str, model: str = "moonshot-v1-8k", temperature: float = 0.3) -> str:
        """
        发送请求并获取 Kimi 的回复
        :param content: 用户输入的内容
        :param model: 使用的模型，默认为 moonshot-v1-8k
        :param temperature: 温度参数，控制生成的随机性
        :return: Kimi 的回复内容
        """
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": content}
                ],
                temperature=temperature,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
