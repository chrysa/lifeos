"""Application orchestrator.

Wires the loaded :class:`~lifeos.config.settings.Settings` together and runs
the assistant. This is a headless-first core: the optional floating overlay UI
(``[ui]`` extra) is layered on top when available, and the application degrades
gracefully to headless when it is not.
"""

from __future__ import annotations

import logging

from lifeos.config.settings import Settings

logger = logging.getLogger(__name__)


class Application:
    """Top-level application lifecycle."""

    def __init__(
        self,
        settings: Settings,
        enable_ui: bool = True,
        debug: bool = False,
    ) -> None:
        self._settings = settings
        self._enable_ui = enable_ui
        self._debug = debug

    def enabled_plugins(self) -> list[str]:
        """Return the names of plugins enabled in the settings."""
        plugins = self._settings.plugins
        return sorted(
            name
            for name, config in plugins.model_dump().items()
            if config.get("enabled", False)
        )

    def run(self) -> None:
        """Start the application and block until it stops.

        This headless core logs its resolved configuration and returns. Richer
        run loops (overlay UI, plugin workers) build on this entry point.
        """
        logger.info(
            "LifeOS starting (ui=%s, debug=%s)",
            self._enable_ui,
            self._debug,
        )
        enabled = self.enabled_plugins()
        if enabled:
            logger.info("Enabled plugins: %s", ", ".join(enabled))
        else:
            logger.info("No plugins enabled")
        if self._enable_ui:
            logger.warning(
                "Overlay UI not available in this build — running headless. "
                "Install the [ui] extra to enable it."
            )
        logger.info("LifeOS ready")
