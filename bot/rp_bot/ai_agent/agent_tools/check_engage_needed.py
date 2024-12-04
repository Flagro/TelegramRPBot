from .base_tool import BaseTool


class CheckEngageNeededTool(BaseTool):
    def run(self, prompt: str) -> bool:
        """
        Returns True if the prompt contains a question or a request for information.
        """
        return self.ask_yes_no_question(prompt)
