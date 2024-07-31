import logging
from decouple import config
from pathlib import Path

from bot.rp_bot.bot import RPBot
from bot.models.config import (
    TGConfig,
    BotConfig,
    DefaultChatModes,
    LocalizerTranslations,
    AIConfig,
)
from bot.telegram.bot import TelegramBot


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

    rp_bot = RPBot(
        db_user=config("DB_USER"),
        db_password=config("DB_PASSWORD"),
        db_host=config("DB_HOST"),
        db_port=config("DB_PORT"),
        db_name=config("DB_NAME"),
        openai_api_key=config("OPENAI_API_KEY"),
        translations=translations,
        default_chat_modes=default_chat_modes,
        ai_config=ai_config,
        bot_config=bot_config,
        allowed_handles=config("ALLOWED_HANDLES", "").split(",") or None,
        admin_handles=config("ADMIN_HANDLES", "").split(",") or None,
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
