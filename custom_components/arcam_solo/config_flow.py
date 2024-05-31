"""Config flow for Arcam Solo."""
from __future__ import annotations

import asyncio
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.helpers import selector

from pyarcamsolo import ArcamSolo

from .const import DOMAIN, DEFAULT_CONF_SCAN_INTERVAL, CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES

_LOGGER = logging.getLogger(__name__)

class ArcamSoloFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Arcam Solo."""

    VERSION = 1

    async def async_step_user(
            self,
            user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            arcam = ArcamSolo(
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT]
            )
            try:
                # await arcam.connect(reconnect=False)
                # await asyncio.sleep(5) # allow init queries to run
                # await arcam.shutdown()
                return self.async_create_entry(
                    title=f"{user_input[CONF_HOST]}:{int(user_input[CONF_PORT])}",
                    data=user_input
                )
            except Exception as exc:
                await arcam.shutdown()
                _LOGGER.warning("Arcam Solo Error raised: %s", exc)
                _errors["base"] = f"Unknown: {exc}"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=(user_input or {}).get(CONF_NAME)
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        )
                    ),
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST)
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        )
                    ),
                    vol.Required(
                        CONF_PORT,
                        default=(user_input or {}).get(CONF_PORT)
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            mode=selector.NumberSelectorMode.BOX,
                            max=65535,
                            min=1000
                        )
                    ),
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=(user_input or {}).get(CONF_SCAN_INTERVAL, DEFAULT_CONF_SCAN_INTERVAL)
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            mode=selector.NumberSelectorMode.BOX,
                            min=120
                        )
                    ),
                    vol.Optional(
                        CONF_ENABLED_FEATURES,
                        default=(user_input or {}).get(CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES)
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=DEFAULT_CONF_ENABLED_FEATURES,
                            multiple=True,
                            mode=selector.SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            ),
            errors=_errors
        )
