import yaml

from pydantic import BaseModel


class BaseYAMLConfigModel(BaseModel):
    """Base model with a load method for loading from a yaml file."""

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, "r") as file:
            config_dict = yaml.safe_load(file)
            if cls.__name__ in config_dict:
                return cls(**config_dict[cls.__name__])
            else:
                raise KeyError(f"{cls.__name__} not found in {file_path}")
