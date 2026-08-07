"""Application settings loaded from a TOML config file.

The config file is optional: when absent, sensible defaults are used so the
application always has a valid :class:`Settings` instance to run with.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "lifeos" / "config.toml"


class PluginConfig(BaseModel):
    """Configuration for a single plugin."""

    enabled: bool = False


class PluginsConfig(BaseModel):
    """Configuration for all known plugins."""

    discord: PluginConfig = Field(default_factory=PluginConfig)
    github: PluginConfig = Field(default_factory=PluginConfig)
    notion: PluginConfig = Field(default_factory=PluginConfig)


class Settings(BaseModel):
    """Top-level application settings."""

    plugins: PluginsConfig = Field(default_factory=PluginsConfig)


def load_config(config_path: Path | None = None) -> Settings:
    """Load settings from ``config_path`` (or the default location).

    Returns default :class:`Settings` when the file does not exist.
    """
    path = config_path or DEFAULT_CONFIG_PATH
    if not path.exists():
        return Settings()
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return Settings.model_validate(data)
