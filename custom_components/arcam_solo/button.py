"""Arcam Solo button entities."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyarcamsolo import ArcamSolo

from .const import DOMAIN, COMMAND_BUTTONS, CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES
from .device import ArcamSoloDevice

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Arcam Solo remote."""
    if "virtual_buttons" in config_entry.data.get(CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES):
        arcam = hass.data[DOMAIN][config_entry.entry_id]
        entities = []
        for conf in COMMAND_BUTTONS:
            entities.append(ArcamCommandButton(
                amp=arcam,
                config_entry=config_entry,
                zone=1,
                btn_config=conf
            ))
        async_add_entities(entities)

class ArcamCommandButton(ArcamSoloDevice, ButtonEntity):
    """Represents a command button."""

    _attr_has_entity_name = True

    def __init__(self,
                 amp: ArcamSolo,
                 config_entry: ConfigEntry,
                 zone: int,
                 btn_config: dict) -> None:
        """Initialize the Arcam Solo."""
        super().__init__(amp, config_entry, zone)
        self._attr_name = btn_config["name"]
        self._attr_icon = btn_config["icon"]
        self._attr_unique_id = f"{self.config_entry.entry_id}-{self.zone}-button-{btn_config['unique_id']}"
        self._ir_command = btn_config["ir_command"]

    @property
    def available(self) -> bool:
        """Return if the entity is currently available."""
        state = self.amp.zones.get(self.zone)
        if state is None:
            return False
        if "power" not in state:
            return False
        if state["power"] == "Standby":
            return False
        return True

    async def async_press(self) -> None:
        """Handle button press."""
        await self.amp.send_ir_command(command=self._ir_command)
