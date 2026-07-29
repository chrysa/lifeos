"""Tests for lifeos package."""

from __future__ import annotations

from pytest_mock import MockerFixture

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


def test_cli_run_headless_mocked(mocker: MockerFixture) -> None:
    from click.testing import CliRunner

    from lifeos.cli import main

    mock_app = mocker.MagicMock()
    mock_app.run.return_value = None
    mock_app_cls = mocker.MagicMock(return_value=mock_app)
    mock_load_config = mocker.MagicMock(return_value=mocker.MagicMock())

    mocker.patch.dict(
        "sys.modules",
        {
            "lifeos.app": mocker.MagicMock(Application=mock_app_cls),
            "lifeos.config": mocker.MagicMock(),
            "lifeos.config.settings": mocker.MagicMock(load_config=mock_load_config),
        },
    )
    runner = CliRunner()
    result = runner.invoke(main, ["--headless"])

    assert result.exit_code == 0


def test_cli_run_with_enable(mocker: MockerFixture) -> None:
    from click.testing import CliRunner

    from lifeos.cli import main

    mock_plugin = mocker.MagicMock()
    mock_plugin.enabled = False
    mock_plugins = mocker.MagicMock()
    mock_plugins.discord = mock_plugin
    mock_settings = mocker.MagicMock()
    mock_settings.plugins = mock_plugins
    mock_load_config = mocker.MagicMock(return_value=mock_settings)
    mock_app = mocker.MagicMock()
    mock_app_cls = mocker.MagicMock(return_value=mock_app)

    mocker.patch.dict(
        "sys.modules",
        {
            "lifeos.app": mocker.MagicMock(Application=mock_app_cls),
            "lifeos.config": mocker.MagicMock(),
            "lifeos.config.settings": mocker.MagicMock(load_config=mock_load_config),
        },
    )
    runner = CliRunner()
    result = runner.invoke(main, ["--headless", "--enable", "discord"])

    assert result.exit_code == 0
