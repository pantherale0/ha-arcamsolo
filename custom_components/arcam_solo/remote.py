"""Virtual remote entity."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.remote import RemoteEntity
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNKNOWN, CONF_NAME
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import ArcamSoloDevice

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Arcam Solo remote."""
    arcam = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            ArcamRemoteEntity(
                amp=arcam,
                config_entry=config_entry,
                zone=1 # multi-zone not supported yet
            )
        ]
    )

class ArcamRemoteEntity(ArcamSoloDevice, RemoteEntity):
    """Represent Arcam Solo remote."""

    @property
    def is_on(self) -> bool:
        """Return true if device on."""
        state = self.amp.zones.get(self.zone)
        if state is None:
            return STATE_UNKNOWN
        if "power" not in state:
            return STATE_UNKNOWN
        return state["power"] != "Standby"

    @property
    def unique_id(self) -> str:
        """Unique ID of the entity."""
        return f"{self.config_entry.entry_id}-{self.zone}-remote"

    @property
    def name(self) -> str:
        """Return entity name."""
        return self.config_entry.data[CONF_NAME]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.amp.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.amp.turn_off()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the device."""
        for com in command:
            try:
                await self.amp.send_ir_command(command=com)
            except ValueError as err:
                raise ServiceValidationError(err) from err
