from telegram.ext import filters

import logging
from collections import namedtuple
from typing import List, Optional

from .handler_decorators import (
    command_handler,
    callback_handler,
    message_handler,
)
from .db import DB
from .ai import AI
from .localizer import Localizer
from .auth import authorized
from .keyboards import get_chat_modes_keyboard


CommandResponse = namedtuple("CommandResponse", ["text", "kwargs", "markup"])
MessageResponse = namedtuple("MessageResponse", ["text", "image_url"])


class RPBot:
    def __init__(
        self,
        db: DB,
        ai: AI,
    ):
        self.db = db
        self.ai = ai
        self.logger = logging.getLogger(f"{__name__}.{id(self)}")

        # Define bot commands
        Command = namedtuple("Command", ["command", "description_tag", "handler"])
        self.commands = [
            Command("reset", "reset_description", self._reset),
            Command("mode", "mode_description", self._mode),
            Command("addmode", "addmode_description", self._addmode),
            Command("deletemode", "deletemode_description", self._deletemode),
            Command("introduce", "introduce_description", self._introduce),
            Command("fact", "fact_description", self._fact),
            Command("clearfacts", "clearfacts_description", self._clearfacts),
            Command("usage", "usage_description", self._usage),
            Command("language", "language_description", self._language),
            Command("help", "help_description", self._help),
        ]
        Handler = namedtuple("Handler", ["filters", "handler"])
        self.handlers = [
            Handler(
                (filters.TEXT | filters.VOICE | filters.PHOTO) & ~filters.COMMAND,
                self._get_reply,
            ),
        ]
        Callback = namedtuple("Callbacks", ["pattern", "callback"])
        self.callbacks = [
            Callback("^show_chat_modes", self._show_chat_modes),
            Callback("^set_chat_mode", self._set_chat_mode),
            Callback("^delete_chat_mode", self._delete_chat_mode),
        ]

    @callback_handler
    @authorized
    async def _show_chat_modes(self, chat_id, args) -> CommandResponse:
        button_action = args[0]
        page_index = int(args[1])
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", button_action, page_index
        )
        return CommandResponse("", {}, modes_keyboard)

    @callback_handler
    @authorized
    async def _set_chat_mode(self, chat_id, args) -> CommandResponse:
        mode_id = args[0]
        self.db.set_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_set", {"mode_id": mode_id}, None)

    @callback_handler
    @authorized
    async def _delete_chat_mode(self, chat_id, args) -> CommandResponse:
        mode_id = args[0]
        self.db.delete_chat_mode(chat_id, mode_id)
        return CommandResponse("mode_deleted", {"mode_id": mode_id}, None)

    @command_handler
    @authorized
    async def _mode(self, chat_id) -> CommandResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", "set_chat_mode"
        )
        return CommandResponse("choose_mode", {}, modes_keyboard)

    @command_handler
    @authorized
    async def _addmode(self, chat_id, args) -> CommandResponse:
        mode_description = " ".join(args)
        # Get the first sentence or paragraph of the mode description:
        # TODO: implement NER here
        mode_name = mode_description.split("\n")[0].split(".")[0]
        try:
            self.db.add_chat_mode(chat_id, mode_name, mode_description)
            return CommandResponse("mode_added", {"mode_name": mode_name})
        except ValueError as e:
            self.logger.error(f"Error adding mode: {e}")
            return CommandResponse("inappropriate_mode", {}, None)

    @command_handler
    @authorized
    async def _deletemode(self, chat_id) -> CommandResponse:
        available_modes = self.db.get_chat_modes(chat_id)
        modes_keyboard = get_chat_modes_keyboard(
            available_modes, "show_chat_modes", "delete_chat_mode"
        )
        return CommandResponse("choose_mode_to_delete", {}, modes_keyboard)

    @command_handler
    @authorized
    async def _introduce(self, chat_id, user_handle, args) -> CommandResponse:
        introduction = " ".join(args)
        try:
            self.db.add_introduction(chat_id, user_handle, introduction)
            return CommandResponse("introduction_added", {"user_handle": user_handle})
        except ValueError as e:
            self.logger.error(f"Error adding introduction: {e}")
            return CommandResponse("inappropriate_introduction", {}, None)

    @command_handler
    @authorized
    async def _fact(self, chat_id, args) -> CommandResponse:
        facts_user_handle = args[0]
        facts = " ".join(args[1:])
        try:
            self.db.add_fact(chat_id, facts_user_handle, facts)
            return CommandResponse("fact_added", {"user_handle": facts_user_handle})
        except ValueError as e:
            self.logger.error(f"Error adding fact: {e}")
            return CommandResponse("inappropriate_fact", {}, None)

    @command_handler
    @authorized
    async def _clearfacts(self, chat_id, args) -> CommandResponse:
        facts_user_handle = args[0]
        self.db.clear_facts(chat_id, facts_user_handle)
        return CommandResponse(
            "facts_cleared", {"user_handle": facts_user_handle}, None
        )

    @command_handler
    @authorized
    async def _usage(self, user_handle) -> CommandResponse:
        user_usage = self.db.get_user_usage(user_handle)
        return CommandResponse("usage_text", user_usage._asdict(), None)

    @command_handler
    @authorized
    async def _language(self, chat_id, args) -> CommandResponse:
        language = args[0]
        try:
            self.localizer.set_language(chat_id, language)
            return CommandResponse("language_set", {"language": language})
        except ValueError as e:
            self.logger.error(f"Error setting language: {e}")
            return CommandResponse("language_set_error", {"language": language}, None)

    @command_handler
    @authorized
    async def _reset(self, chat_id) -> CommandResponse:
        self.db.reset(chat_id)
        return CommandResponse("reset_done", {}, None)

    @command_handler
    async def _help(self) -> CommandResponse:
        return CommandResponse("help_text", {}, None)

    @message_handler
    @authorized
    async def _get_reply(
        self, chat_id, thread_id, is_bot_mentioned, user_handle, message, image, voice
    ) -> Optional[MessageResponse]:
        if self.telegram_bot_config.track_conversation_thread:
            self.db.save_thread_message(thread_id, user_handle, message)
        if not is_bot_mentioned:
            return None
        
        image_description = None
        if image:
            image_description = await self.ai.describe_image(image)
        voice_description = None
        if voice:
            voice_description = await self.ai.transcribe_audio(voice)
        self.db.add_user_input_to_dialog(
            chat_id, user_handle, message, image_description, voice_description
        )
        user_input = self.localizer.compose_user_input(
            message, image_description, voice_description
        )
        response_message, response_image_url = await self.ai.get_reply(
            chat_id, thread_id, user_handle, user_input
        )
        self.db.add_bot_response_to_dialog(
            chat_id, response_message, response_image_url
        )
        return MessageResponse(response_message, response_image_url)
