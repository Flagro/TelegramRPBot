from pydantic import BaseModel


class AuthConfig(BaseModel):
    allowed_handles: str
    admin_handles: str
