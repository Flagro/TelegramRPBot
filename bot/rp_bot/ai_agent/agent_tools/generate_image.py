from langchain.chains import LLMChain
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

from .base_tool import BaseTool


class ImageGeneratorTool(BaseTool):
    def __init__(self, model: OpenAI):
        super().__init__(model)

    def run(self, prompt: str) -> str:
        """
        Returns the URL of the generated image based on the prompt.
        """
        image_description_generation_prompt = PromptTemplate(
            input_variables=["image_description"],
            template="Generate a detailed prompt to generate an image based on the description: {image_description}",
        )
        image_chain = LLMChain(llm=self.llm, prompt=image_description_generation_prompt)
        image_url = DallEAPIWrapper().run(image_chain.run(prompt))
        return image_url
