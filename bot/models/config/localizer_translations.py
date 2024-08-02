from .base_config import BaseYAMLConfigModel
from pydantic import BaseModel
from typing import Dict, Optional
import yaml


class LocalizerTranslation(BaseModel):
    language_translation: Dict[str, str]


class LocalizerTranslations(BaseYAMLConfigModel):
    translations: Dict[str, LocalizerTranslation]

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, "r") as file:
            config_dict = yaml.safe_load(file)
            if "LocalizerTranslations" in config_dict:
                translations_dict = config_dict["LocalizerTranslations"]
                translations = {
                    key: LocalizerTranslation(language_translation=value)
                    for key, value in translations_dict.items()
                }
                return cls(translations=translations)
            else:
                raise KeyError(f"LocalizerTranslations not found in {file_path}")
