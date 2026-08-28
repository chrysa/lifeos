"""Tests for lifeos package."""

from __future__ import annotations

from pytest_mock import MockerFixture

import lifeos
from lifeos import __author__, __version__
from lifeos.app import Application
from lifeos.config.settings import Settings, load_config


def test_version_string() -> None:
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_author_string() -> None:
    assert isinstance(__author__, str)


def test_package_exports_version() -> None:
    assert hasattr(lifeos, "__version__")


def test_cli_importable() -> None:
    from lifeos.cli import main

    assert callable(main)


def test_cli_help() -> None:
    from click.testing import CliRunner

    from lifeos.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "lifeos" in result.output.lower() or "Usage" in result.output


def test_cli_version() -> None:
    from click.testing import CliRunner

    from lifeos.cli import main

    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_main_module_importable() -> None:
    import importlib

    import lifeos.__main__ as lm  # noqa: F401

    importlib.import_module("lifeos.__main__")


def test_cli_run_headless(mocker: MockerFixture) -> None:
    from click.testing import CliRunner

    from lifeos.cli import main

    run_spy = mocker.spy(Application, "run")
    runner = CliRunner()
    result = runner.invoke(main, ["--headless"])

    assert result.exit_code == 0, result.output
    run_spy.assert_called_once()


def test_cli_run_with_enable(mocker: MockerFixture) -> None:
    from click.testing import CliRunner

    from lifeos.cli import main

    captured: dict[str, Application] = {}
    original_run = Application.run

    def _capture(self: Application) -> None:
        captured["app"] = self
        original_run(self)

    mocker.patch.object(Application, "run", _capture)
    runner = CliRunner()
    result = runner.invoke(main, ["--headless", "--enable", "discord"])

    assert result.exit_code == 0, result.output
    assert captured["app"].enabled_plugins() == ["discord"]


def test_load_config_defaults_when_missing(tmp_path: object) -> None:
    from pathlib import Path

    missing = Path(str(tmp_path)) / "does-not-exist.toml"
    settings = load_config(config_path=missing)

    assert isinstance(settings, Settings)
    assert settings.plugins.discord.enabled is False


def test_load_config_reads_toml(tmp_path: object) -> None:
    from pathlib import Path

    config = Path(str(tmp_path)) / "config.toml"
    config.write_text("[plugins.discord]\nenabled = true\n")
    settings = load_config(config_path=config)

    assert settings.plugins.discord.enabled is True
    assert settings.plugins.notion.enabled is False


def test_application_enabled_plugins_empty() -> None:
    app = Application(settings=Settings(), enable_ui=False)

    assert app.enabled_plugins() == []


def test_application_run_headless(caplog: object) -> None:
    import logging

    settings = Settings()
    settings.plugins.notion.enabled = True
    app = Application(settings=settings, enable_ui=False, debug=True)

    with caplog.at_level(logging.INFO):  # type: ignore[attr-defined]
        app.run()

    assert app.enabled_plugins() == ["notion"]


def test_application_run_with_ui_warns(caplog: object) -> None:
    import logging

    app = Application(settings=Settings(), enable_ui=True)

    with caplog.at_level(logging.WARNING):  # type: ignore[attr-defined]
        app.run()

    assert any("headless" in record.message for record in caplog.records)  # type: ignore[attr-defined]
