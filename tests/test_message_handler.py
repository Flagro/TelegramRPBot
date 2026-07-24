from datetime import datetime
from logging import getLogger
from types import SimpleNamespace

import pytest

from bot.models.handlers_input import Context, Message, Person, TranscribedMessage
from bot.rp_bot.ai_agent.agent_tools.agent import AIAgentStreamingResponse, ChatFact
from bot.rp_bot.messages.message_handler import MessageHandler


class FakeChats:
    def __init__(
        self,
        *,
        chat_started: bool = True,
        conversation_tracker_enabled: bool = False,
        autoengage_enabled: bool = False,
        autofact_enabled: bool = False,
    ) -> None:
        self.chat_started = chat_started
        self.conversation_tracker_enabled = conversation_tracker_enabled
        self.autoengage_enabled = autoengage_enabled
        self.autofact_enabled = autofact_enabled

    async def get_conversation_tracker_state(self, context: Context) -> bool:
        return self.conversation_tracker_enabled

    async def chat_is_started(self, context: Context) -> bool:
        return self.chat_started

    async def get_autoengage_state(self, context: Context) -> bool:
        return self.autoengage_enabled

    async def get_auto_fact_state(self, context: Context) -> bool:
        return self.autofact_enabled


class FakeDialogs:
    def __init__(self) -> None:
        self.messages = []

    async def add_message_to_dialog(
        self,
        *,
        context: Context,
        person: Person | str,
        transcribed_message: TranscribedMessage,
    ) -> None:
        self.messages.append(
            {
                "context": context,
                "person": person,
                "transcribed_message": transcribed_message,
            }
        )


class FakeUserUsage:
    def __init__(self, *, usage: float = 0, limit: float = 100) -> None:
        self.usage = usage
        self.limit = limit
        self.added_points = []

    async def get_user_usage(self, person: Person) -> float:
        return self.usage

    async def get_user_usage_limit(self, person: Person) -> float:
        return self.limit

    async def add_usage_points(self, person: Person, points: float) -> None:
        self.added_points.append({"person": person, "points": points})


class FakeUserFacts:
    def __init__(self) -> None:
        self.facts = []

    async def add_fact(
        self,
        *,
        context: Context,
        facts_user_handle: str,
        fact: str,
        created_by: str,
    ) -> None:
        self.facts.append(
            {
                "context": context,
                "facts_user_handle": facts_user_handle,
                "fact": fact,
                "created_by": created_by,
            }
        )


class FakeModelsToolkit:
    def __init__(self, *, estimated_price: float = 1) -> None:
        self.estimated_price = estimated_price
        self.text_model = SimpleNamespace(
            async_ask_yes_no_question=self.async_ask_yes_no_question
        )

    def estimate_price(self, **kwargs) -> float:
        return self.estimated_price

    async def async_ask_yes_no_question(self, question: str) -> bool:
        return False


def build_handler(
    *,
    chat_started: bool = True,
    conversation_tracker_enabled: bool = False,
    autoengage_enabled: bool = False,
    autofact_enabled: bool = False,
    usage: float = 0,
    limit: float = 100,
    estimated_price: float = 1,
) -> MessageHandler:
    db = SimpleNamespace(
        chats=FakeChats(
            chat_started=chat_started,
            conversation_tracker_enabled=conversation_tracker_enabled,
            autoengage_enabled=autoengage_enabled,
            autofact_enabled=autofact_enabled,
        ),
        dialogs=FakeDialogs(),
        user_usage=FakeUserUsage(usage=usage, limit=limit),
        user_facts=FakeUserFacts(),
    )
    return MessageHandler(
        db=db,
        models_toolkit=FakeModelsToolkit(estimated_price=estimated_price),
        localizer=None,
        prompt_manager=None,
        memory_manager=None,
        auth=None,
        bot_config=None,
        logger=getLogger("test-message-handler"),
    )


async def collect_stream(handler: MessageHandler, person: Person, context: Context):
    message = Message(message_text="hello", timestamp=datetime(2026, 7, 24))
    return [
        response
        async for response in handler.stream_get_response(
            person=person,
            context=context,
            message=message,
            args=[],
        )
    ]


@pytest.fixture
def person() -> Person:
    return Person(telegram_id=42, user_handle="@ada")


def context(*, is_bot_mentioned: bool = True) -> Context:
    return Context(chat_id=100, is_bot_mentioned=is_bot_mentioned)


@pytest.mark.asyncio
async def test_stream_get_response_ignores_messages_when_chat_is_stopped(person):
    handler = build_handler(chat_started=False)

    responses = await collect_stream(handler, person, context(is_bot_mentioned=True))

    assert responses == []
    assert handler.db.dialogs.messages == []


@pytest.mark.asyncio
async def test_stream_get_response_saves_context_without_ai_when_not_mentioned(person):
    handler = build_handler(conversation_tracker_enabled=True)

    responses = await collect_stream(handler, person, context(is_bot_mentioned=False))

    assert responses == []
    assert len(handler.db.dialogs.messages) == 1
    saved_message = handler.db.dialogs.messages[0]
    assert saved_message["person"] == person
    assert saved_message["transcribed_message"].message_text == "hello"
    assert handler.db.user_usage.added_points == []


@pytest.mark.asyncio
async def test_stream_get_response_blocks_when_usage_limit_would_be_exceeded(person):
    handler = build_handler(usage=9, limit=10, estimated_price=2)

    responses = await collect_stream(handler, person, context(is_bot_mentioned=True))

    assert len(responses) == 1
    assert responses[0].text == "usage_limit_exceeded"
    assert responses[0].kwargs == {"user_handle": "@ada", "usage_limit": 10}
    assert handler.db.dialogs.messages == []
    assert handler.db.user_usage.added_points == []


@pytest.mark.asyncio
async def test_stream_get_response_records_dialog_usage_and_facts_after_agent_response(
    monkeypatch,
    person,
):
    class FakeAIAgent:
        def __init__(self, **kwargs) -> None:
            self.kwargs = kwargs

        async def astream(self):
            yield AIAgentStreamingResponse(
                total_text="Bot reply",
                total_price=3.5,
                transcribed_user_message=TranscribedMessage(
                    message_text="User transcript",
                    timestamp=datetime(2026, 7, 24),
                ),
                image_description="Generated image",
                audio_description="Generated audio",
                generated_facts=[
                    ChatFact(user_handle="@ada", user_fact="Ada likes tests.")
                ],
            )

    monkeypatch.setattr(
        "bot.rp_bot.messages.message_handler.AIAgent",
        FakeAIAgent,
    )
    handler = build_handler(autofact_enabled=True)

    responses = await collect_stream(handler, person, context(is_bot_mentioned=True))

    assert len(responses) == 1
    assert responses[0].text == "streaming_message_response"
    assert responses[0].kwargs == {"response_text": "Bot reply"}
    assert handler.db.user_usage.added_points == [{"person": person, "points": 3.5}]
    assert len(handler.db.dialogs.messages) == 2
    assert handler.db.dialogs.messages[0]["person"] == person
    assert (
        handler.db.dialogs.messages[0]["transcribed_message"].message_text
        == "User transcript"
    )
    assert handler.db.dialogs.messages[1]["person"] == "bot"
    assert (
        handler.db.dialogs.messages[1]["transcribed_message"].message_text
        == "Bot reply"
    )
    assert handler.db.user_facts.facts == [
        {
            "context": context(is_bot_mentioned=True),
            "facts_user_handle": "@ada",
            "fact": "Ada likes tests.",
            "created_by": "autofact",
        }
    ]
