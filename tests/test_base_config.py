from pathlib import Path

import pytest

from bot.models.config.base_config import BaseYAMLConfigModel


class ExampleConfig(BaseYAMLConfigModel):
    value: str
    count: int


def test_base_yaml_config_model_loads_matching_section(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "ExampleConfig:\n"
        "  value: test\n"
        "  count: 3\n"
    )

    config = ExampleConfig.load(config_file)

    assert config.value == "test"
    assert config.count == 3


def test_base_yaml_config_model_raises_for_missing_section(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("OtherConfig:\n  value: test\n")

    with pytest.raises(KeyError, match="ExampleConfig not found"):
        ExampleConfig.load(config_file)
