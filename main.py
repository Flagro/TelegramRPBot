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
    
    # chat_modes
    with open(config_dir / "chat_modes.yml", 'r') as f:
        chat_modes = yaml.safe_load(f)

    # default models
    with open(config_dir / "models.yml", 'r') as f:
        models = yaml.safe_load(f)

    db = DB(config("DB_URI"))

    ai = AI(openai_api_key=config("OPENAI_API_KEY"),
            db=db,
            ai_config)
    
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
