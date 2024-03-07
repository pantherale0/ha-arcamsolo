"""Config flow for Arcam Solo."""
from __future__ import annotations

import asyncio
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.helpers import selector

from pyarcamsolo import ArcamSolo

from .const import DOMAIN

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
            try:
                arcam = ArcamSolo(
                    host=user_input[CONF_HOST],
                    port=user_input[CONF_PORT]
                )
                await arcam.connect()
                await asyncio.sleep(4) # allow init queries to run
                await arcam.shutdown()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )
            except Exception as exc:
                _LOGGER.warning("Arcam Solo Error raised: %s", exc)
                _errors["base"] = "unknown"

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
                }
            ),
            errors=_errors
        )
