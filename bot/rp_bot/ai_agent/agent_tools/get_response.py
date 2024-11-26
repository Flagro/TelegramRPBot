from .base_tool import BaseTool


class GetResponseTool(BaseTool):
    async def run(self, user_input: str) -> str:
        """
        Returns the response to the user input.
        """
        return await self.llm.ainvoke(user_input)
