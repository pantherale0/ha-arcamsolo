"""Config flow for Arcam Solo."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE, CONF_NAME
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES

_LOGGER = logging.getLogger(__name__)

class ArcamSoloFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Arcam Solo."""

    VERSION = 2

    async def async_step_user(
            self,
            user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=f"{user_input[CONF_NAME]}",
                data=user_input
            )
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
                        CONF_DEVICE,
                        default=(user_input or {}).get(CONF_DEVICE)
                    ): selector.SerialPortSelector(),
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
