from .base_config import BaseYAMLConfigModel
from pydantic import BaseModel, Field
from typing import Dict


class LocalizerTranslation(BaseModel):
    english: str = Field(..., alias='english')

    class Config:
        allow_population_by_field_name = True

class LocalizerTranslations(BaseYAMLConfigModel):
    translations: Dict[str, LocalizerTranslation]
