"""Tests for lifeos package."""

from __future__ import annotations

import lifeos
from lifeos import __author__, __version__


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


def test_cli_run_headless_mocked() -> None:
    from unittest.mock import MagicMock, patch

    from click.testing import CliRunner

    from lifeos.cli import main

    mock_app = MagicMock()
    mock_app.run.return_value = None
    mock_app_cls = MagicMock(return_value=mock_app)
    mock_load_config = MagicMock(return_value=MagicMock())

    with patch.dict(
        "sys.modules",
        {
            "lifeos.app": MagicMock(Application=mock_app_cls),
            "lifeos.config": MagicMock(),
            "lifeos.config.settings": MagicMock(load_config=mock_load_config),
        },
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--headless"])

    assert result.exit_code == 0


def test_cli_run_with_enable() -> None:
    from unittest.mock import MagicMock, patch

    from click.testing import CliRunner

    from lifeos.cli import main

    mock_plugin = MagicMock()
    mock_plugin.enabled = False
    mock_plugins = MagicMock()
    mock_plugins.discord = mock_plugin
    mock_settings = MagicMock()
    mock_settings.plugins = mock_plugins
    mock_load_config = MagicMock(return_value=mock_settings)
    mock_app = MagicMock()
    mock_app_cls = MagicMock(return_value=mock_app)

    with patch.dict(
        "sys.modules",
        {
            "lifeos.app": MagicMock(Application=mock_app_cls),
            "lifeos.config": MagicMock(),
            "lifeos.config.settings": MagicMock(load_config=mock_load_config),
        },
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--headless", "--enable", "discord"])

    assert result.exit_code == 0
