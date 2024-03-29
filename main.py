import logging
import yaml
from decouple import config
from pathlib import Path

from bot import TelegramRPBot
from bot.ai import AI
from bot.db import DB
from bot.localizer import Localizer


def main():
    # init logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    
    # load config dir
    config_dir = Path(__file__).parent.resolve() / "config"
    
    # ai config
    with open(config_dir / "ai_config.yaml", 'r') as f:
        ai_config = yaml.safe_load(f)
        
    # db config
    with open(config_dir / "db_config.yaml", 'r') as f:
        db_config = yaml.safe_load(f)
    
    # default chat_modes
    with open(config_dir / "default_chat_modes.yaml", 'r') as f:
        default_chat_modes = yaml.safe_load(f)

    # localizer translations
    with open(config_dir / "localizer_translations.yaml", 'r') as f:
        translations = yaml.safe_load(f)
        
    # telegram bot config
    with open(config_dir / "telegram_bot_config.yaml", 'r') as f:
        telegram_bot_config = yaml.safe_load(f)

    db = DB(config("DB_URI"))

    ai = AI(openai_api_key=config("OPENAI_API_KEY"),
            db=db)
    
    localizer = Localizer()

    bot = TelegramRPBot(
        telegram_token=config("TELEGRAM_TOKEN"),
        allowed_handles=config("ALLOWED_HANDLES").split(","),
        admin_handles=config("ADMIN_HANDLES").split(","),
        db=db,
        ai=ai,
        localizer=localizer,
    )
    bot.run()


if __name__ == "__main__":
    main()
