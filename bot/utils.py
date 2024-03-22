from __future__ import annotations

import io
import asyncio
import logging

import telegram
from telegram import Update, ChatMember, constants
from telegram.ext import CallbackContext, ContextTypes


def bot_mentioned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    is_private_chat = update.message.chat.type == "private"
    is_bot_mentioned = (
        update.message.text is not None
        and ("@" + context.bot.username) in update.message.text
    )
    bot_in_reply_tree = (
        update.message.reply_to_message is not None
        and update.message.reply_to_message.from_user.id == context.bot.id
    )
    return not (is_private_chat or bot_in_reply_tree or is_bot_mentioned)


async def get_file_in_memory(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> io.BytesIO:
    file = await context.bot.getFile(file_id)
    file_stream = io.BytesIO()
    await file.download(out=file_stream)
    file_stream.seek(0)
    return file_stream


async def is_user_in_group(
    update: Update, context: CallbackContext, user_id: int
) -> bool:
    """
    Checks if user_id is a member of the group
    """
    try:
        chat_member = await context.bot.get_chat_member(update.message.chat_id, user_id)
        return chat_member.status in [
            ChatMember.OWNER,
            ChatMember.ADMINISTRATOR,
            ChatMember.MEMBER,
        ]
    except telegram.error.BadRequest as e:
        if str(e) == "User not found":
            return False
        else:
            raise e
    except Exception as e:
        raise e


def get_thread_id(update: Update) -> int | None:
    """
    Gets the message thread id for the update, if any
    """
    if update.effective_message and update.effective_message.is_topic_message:
        return update.effective_message.message_thread_id
    return None


def get_stream_cutoff_values(update: Update, content: str) -> int:
    """
    Gets the stream cutoff values for the message length
    """
    if is_group_chat(update):
        # group chats have stricter flood limits
        return (
            180
            if len(content) > 1000
            else 120 if len(content) > 200 else 90 if len(content) > 50 else 50
        )
    return (
        90
        if len(content) > 1000
        else 45 if len(content) > 200 else 25 if len(content) > 50 else 15
    )


def split_into_chunks(text: str, chunk_size: int = 4096) -> list[str]:
    """
    Splits a string into chunks of a given size.
    """
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


async def wrap_with_indicator(
    update: Update,
    context: CallbackContext,
    coroutine,
    chat_action: constants.ChatAction = "",
    is_inline=False,
):
    """
    Wraps a coroutine while repeatedly sending a chat action to the user.
    """
    task = context.application.create_task(coroutine(), update=update)
    while not task.done():
        if not is_inline:
            context.application.create_task(
                update.effective_chat.send_action(
                    chat_action, message_thread_id=get_thread_id(update)
                )
            )
        try:
            await asyncio.wait_for(asyncio.shield(task), 4.5)
        except asyncio.TimeoutError:
            pass


async def edit_message_with_retry(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int | None,
    message_id: str,
    text: str,
    markdown: bool = True,
    is_inline: bool = False,
):
    """
    Edit a message with retry logic in case of failure (e.g. broken markdown)
    :param context: The context to use
    :param chat_id: The chat id to edit the message in
    :param message_id: The message id to edit
    :param text: The text to edit the message with
    :param markdown: Whether to use markdown parse mode
    :param is_inline: Whether the message to edit is an inline message
    :return: None
    """
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=int(message_id) if not is_inline else None,
            inline_message_id=message_id if is_inline else None,
            text=text,
            parse_mode=constants.ParseMode.MARKDOWN if markdown else None,
        )
    except telegram.error.BadRequest as e:
        if str(e).startswith("Message is not modified"):
            return
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=int(message_id) if not is_inline else None,
                inline_message_id=message_id if is_inline else None,
                text=text,
            )
        except Exception as e:
            logging.warning(f"Failed to edit message: {str(e)}")
            raise e

    except Exception as e:
        logging.warning(str(e))
        raise e
