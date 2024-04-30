import logging
from decouple import config
from pathlib import Path

from bot.rp_bot.ai import AI
from bot.rp_bot.db import DB
from bot.rp_bot.auth import Auth
from bot.rp_bot.localizer import Localizer
from bot.models.config import (
    TGConfig,
    DefaultChatModes,
    LocalizerTranslations,
    DBConfig,
    AIConfig,
)


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
    db_config = DBConfig.load(config_dir / "db_config.yaml")
    ai_config = AIConfig.load(config_dir / "ai_config.yaml")

    db = DB(
        config("DB_URI"), db_config=db_config, default_chat_modes=default_chat_modes
    )

    ai = AI(openai_api_key=config("OPENAI_API_KEY"), db=db, ai_config=ai_config)

    localizer = Localizer(db=db, translations=translations)
    
    auth = Auth(allowed_handles=config("ALLOWED_HANDLES").split(","),
                admin_handles=config("ADMIN_HANDLES").split(","))

    bot = TelegramRPBot(
        telegram_token=config("TELEGRAM_TOKEN"),
        db=db,
        ai=ai,
        localizer=localizer,
        telegram_bot_config=telegram_bot_config,
    )
    bot.run()


if __name__ == "__main__":
    main()
