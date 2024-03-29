from __future__ import annotations

import io
import asyncio
import logging

import telegram
from telegram import Update, constants
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


async def get_file_in_memory(
    file_id: str, context: ContextTypes.DEFAULT_TYPE
) -> io.BytesIO:
    file = await context.bot.getFile(file_id)
    file_stream = io.BytesIO()
    await file.download(out=file_stream)
    file_stream.seek(0)
    return file_stream


def get_thread_id(update: Update) -> int | None:
    """
    Gets the message thread id for the update, if any
    """
    if update.effective_message and update.effective_message.is_topic_message:
        return update.effective_message.message_thread_id
    return None


def get_stream_cutoff_values(content: str) -> int:
    """
    Gets the stream cutoff values for the message length
    """
    if len(content) > 1000:
        return 180
    elif len(content) > 200:
        return 120
    elif len(content) > 50:
        return 90
    else:
        return 50


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
