from ...models.base_handlers import BaseCommandHandler
from ...models.handlers_response import CommandResponse
from ...models.handlers_input import Person, Context, Message
from ..auth import BotAdmin


class CommandHandler(BaseCommandHandler):
    permissions = [BotAdmin]
    command = "addmode"
    list_priority_order = 1

    async def get_command_response(self, Person, Context, Message, args) -> CommandResponse:
        mode_description = " ".join(args)
        chat_id = Context.chat_id
        # Get the first sentence or paragraph of the mode description:
        # TODO: implement NER here
        mode_name = mode_description.split("\n")[0].split(".")[0]
        try:
            self.db.add_chat_mode(chat_id, mode_name, mode_description)
            return CommandResponse("mode_added", {"mode_name": mode_name})
        except ValueError as e:
            self.logger.error(f"Error adding mode: {e}")
            return CommandResponse("inappropriate_mode", {}, None)
