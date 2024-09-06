from langchain_core.runnables import chain

from ...db import DB
from ....models.handlers_input import Context


@chain
async def get_chat_facts(db: DB, context: Context) -> str:
    # TODO: pass the user handles
    chat_facts = await db.user_facts.get_chat_facts(context)
    # TODO: the prompt manager should be used for that
    return "The following facts are known about the users in this chat:\n" + "\n".join(
        [f"{user}: {fact}" for user, fact in chat_facts]
    )
