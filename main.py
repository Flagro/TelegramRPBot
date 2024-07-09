import logging
from decouple import config
from pathlib import Path

from bot.rp_bot.ai import AI
from bot.rp_bot.db import DB
from bot.rp_bot.auth import Auth
from bot.models.localizer import Localizer
from bot.rp_bot.bot import RPBot
from bot.models.config import (
    TGConfig,
    DefaultChatModes,
    LocalizerTranslations,
    AIConfig,
)
from bot.telegram.bot import TelegramBot


def main():
    # init logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    config_dir = Path(__file__).parent.resolve() / "config"
    telegram_bot_config = TGConfig.load(config_dir / "tg_config.yaml")
    default_chat_modes = DefaultChatModes.load(config_dir / "default_chat_modes.yaml")
    translations = LocalizerTranslations.load(
        config_dir / "localizer_translations.yaml"
    )
    ai_config = AIConfig.load(config_dir / "ai_config.yaml")

    db = DB(
        db_user=config("DB_USER"),
        db_password=config("DB_PASSWORD"),
        db_host=config("DB_HOST"),
        db_port=config("DB_PORT"),
        db_name=config("DB_NAME"),
        default_chat_modes=default_chat_modes,
    )

    ai = AI(openai_api_key=config("OPENAI_API_KEY"), db=db, ai_config=ai_config)

    localizer = Localizer(translations=translations)

    auth = Auth(
        allowed_handles=config("ALLOWED_HANDLES").split(","),
        admin_handles=config("ADMIN_HANDLES").split(","),
    )

    rp_bot = RPBot(
        ai=ai, db=db, localizer=localizer, auth=auth, logger=logging.getLogger("RPBot")
    )

    tg_bot = TelegramBot(
        telegram_token=config("TELEGRAM_BOT_TOKEN"),
        bot=rp_bot,
        localizer=localizer,
        telegram_bot_config=telegram_bot_config,
    )
    tg_bot.run()


if __name__ == "__main__":
    main()
