import logging
import yaml
from decouple import config
from pathlib import Path

from bot import TelegramRPBot


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

    # models
    with open(config_dir / "models.yml", 'r') as f:
        models = yaml.safe_load(f)


    ai = AI(openai_api_key=config("OPENAI_API_KEY"))
    
    db = DB(config("DB_URI"))
    
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
