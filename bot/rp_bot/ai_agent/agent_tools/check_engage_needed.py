from typing import Literal, List
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import chain
from langchain_openai import OpenAI


class EngageNeeded(BaseModel):
    # TODO: move this to prompt manager
    engage_needed: bool = Field(
        description="True if the user prompt requires engagement"
    )


@chain
def check_engage_needed(llm: OpenAI, prompt: str) -> bool:
    """
    Returns True if the prompt contains a question or a request for information.
    """
    parser = JsonOutputParser(pydantic_object=EngageNeeded)

    # TODO: implement the chain
    # engage_needed = ...

    return False
