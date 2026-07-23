import logging
from decouple import config
from pathlib import Path
from typing import Optional
from omnimodkit.ai_config import AIConfig
from bot.rp_bot.bot import get_rp_bot
from bot.models.config import (
    TGConfig,
    BotConfig,
    DefaultChatModes,
    LocalizerTranslations,
)
from bot.telegram.bot import TelegramBot


def parse_handle_list(raw_handles: str) -> Optional[list[str]]:
    handles = [handle.strip() for handle in raw_handles.split(",")]
    handles = [handle for handle in handles if handle]
    if not handles or "*" in handles:
        return None
    return handles


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    config_dir = Path(__file__).parent.resolve() / "config"
    telegram_bot_config = TGConfig.load(config_dir / "tg_config.yaml")
    bot_config = BotConfig.load(config_dir / "bot_config.yaml")
    default_chat_modes = DefaultChatModes.load(config_dir / "default_chat_modes.yaml")
    translations = LocalizerTranslations.load(
        config_dir / "localizer_translations.yaml"
    )
    ai_config = AIConfig.load(config_dir / "ai_config.yaml")

    db_uri = "mongodb://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}".format(
        db_user=config("DB_USER"),
        db_password=config("DB_PASSWORD"),
        db_host=config("DB_HOST"),
        db_port=config("DB_PORT"),
        db_name=config("DB_NAME"),
    )

    rp_bot = get_rp_bot(
        db_uri=db_uri,
        openai_api_key=config("OPENAI_API_KEY"),
        translations=translations,
        default_chat_modes=default_chat_modes,
        ai_config=ai_config,
        bot_config=bot_config,
        allowed_handles=parse_handle_list(config("ALLOWED_HANDLES", "")),
        admin_handles=parse_handle_list(config("ADMIN_HANDLES", "")),
        logger=logging.getLogger("RPBot"),
    )

    tg_bot = TelegramBot(
        telegram_token=config("TELEGRAM_BOT_TOKEN"),
        bot=rp_bot,
        telegram_bot_config=telegram_bot_config,
    )
    tg_bot.run()


if __name__ == "__main__":
    main()
