# **ChatGPT Telegram RP (RolePlay) Bot**: Add a roleplay bot in your group chats

Bring the ability to setup a full roleplay experience in your telegram group chats.

Currently this is the work in progress.

## Features
- Create and use chat-bounded chat modes by describing the agent and how you want it to act
- Introduce yourself to the model
- Add facts about yourself or other people that the model would later use
- Chat with the bot
    - Send it text
    - Send it pictures
    - Send it voice messages
    - Receive back text
    - Receive back puctures
- Flexible tracking of the AI resources usage
- Flexible permissions and limits
- This bot is built with the idea of not being constrained by just Telegram bot, it could be adapted for most other platforms as well.

## Bot commands
- `/start` - Start the bot in current chat
- `/stop` - Stop the bot in current chat
- `/reset` – Reset the dialogue history
- `/mode [mode]` – Select chat mode from existing ones
- `/addmode [mode] [description]` - Add new chat mode
- `/deletemode [mode]` - delete existing chat mode from this chat
- `/introduce [your introduction]` - Add fact about yourself
- `/fact [@tg_handle] [fact]` - add fact about the person within the chat
- `/clearfacts [@tg_handle]` - delete facts for given person
- `/usage` – Show usage limits for your user
- `/language` - Set bot preferred language
- `/conversationtracker` - Turn on/off the conversation tracker for current chat
- `/ban [@tg_handle]` - Ban the user (could work by replying to user's message as well)
- `/unban [@tg_handle]` - Unban the user
- `/help` – Show help

## Setup
1. Get your [OpenAI API](https://openai.com/api/) key

2. Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

3. TODO: add instruction for running the bot
