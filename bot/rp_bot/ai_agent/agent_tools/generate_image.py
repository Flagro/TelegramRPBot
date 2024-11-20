from langchain.chains import LLMChain
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import chain

from .base_tool import BaseTool


@chain
def generate_image(llm: OpenAI, prompt: str) -> str:
    """
    Returns the URL of the generated image based on the prompt.
    """
    image_description_generation_prompt = PromptTemplate(
        input_variables=["image_description"],
        template="Generate a detailed prompt to generate an image based on the description: {image_description}",
    )
    image_chain = LLMChain(llm=llm, prompt=image_description_generation_prompt)
    image_url = DallEAPIWrapper().run(image_chain.run(prompt))
    return image_url


class ImageGeneratorTool(BaseTool):
    def __init__(self, model: OpenAI):
        super().__init__(model)

    def run(self, prompt: str) -> str:
        return generate_image.ainvoke(self.client, prompt)
