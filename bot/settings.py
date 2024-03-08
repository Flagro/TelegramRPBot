import yaml
from decouple import config
from pathlib import Path

# parameters
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
OPENAI_API_KEY = config("OPENAI_API_KEY")
OPENAI_API_BASE = None
ALLOWED_TELEGRAM_USERNAMES = []
NEW_DIALOG_TIMEOUT = 600
ENABLE_MESSAGE_STREAMING = True
RETURN_N_GENERATED_IMAGES = 1
IMAGE_SIZE = "512x512"
N_CHAT_MODES_PER_PAGE = 10
MONGODB_URI = "mongodb://mongo:27017"

# load config
config_dir = Path(__file__).parent.parent.resolve() / "config"

# chat_modes
with open(config_dir / "chat_modes.yml", 'r') as f:
    chat_modes = yaml.safe_load(f)

# models
with open(config_dir / "models.yml", 'r') as f:
    models = yaml.safe_load(f)
