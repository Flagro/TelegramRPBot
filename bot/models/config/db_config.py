from .base_config import BaseYAMLConfigModel


class DBConfig(BaseYAMLConfigModel):
    DB_SCHEME: str
    DB_HOST: str
    DB_PORT: int
