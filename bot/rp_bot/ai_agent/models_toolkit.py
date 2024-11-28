from openai import OpenAI


class ModelsToolkit:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(openai_api_key)
