"""CLI entry point using Click."""

from __future__ import annotations

import logging
from pathlib import Path

import click

from lifeos import __version__


@click.command()
@click.version_option(__version__, prog_name="lifeos")
@click.option(
    "--config",
    "-c",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Path to config.toml (default: ~/.config/lifeos/config.toml)",
)
@click.option(
    "--ui/--headless",
    default=True,
    show_default=True,
    help="Enable floating overlay UI (requires [ui] extra).",
)
@click.option(
    "--enable",
    multiple=True,
    metavar="PLUGIN",
    help="Force-enable plugin(s) regardless of config (e.g. --enable discord).",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable DEBUG logging.",
)
def main(config: Path | None, ui: bool, enable: tuple[str, ...], debug: bool) -> None:
    """LifeOS — floating AI assistant for Linux and Windows."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    from lifeos.app import Application
    from lifeos.config.settings import load_config

    settings = load_config(config_path=config)

    # Force-enable plugins specified via CLI
    for plugin_path in enable:
        parts = plugin_path.split(".")
        obj: object = settings.plugins
        for part in parts[:-1]:
            obj = getattr(obj, part)
        sub = getattr(obj, parts[-1])
        if hasattr(sub, "enabled"):
            sub.enabled = True

    app = Application(settings=settings, enable_ui=ui, debug=debug)
    app.run()
