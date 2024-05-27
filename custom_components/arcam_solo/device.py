"""Represent an Arcam device."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from pyarcamsolo import ArcamSolo

from .const import DOMAIN

class ArcamSoloDevice(Entity):
    """Represent a Arcam entity."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, amp: ArcamSolo, config_entry: ConfigEntry, zone: int) -> None:
        """Initialize a ArcamSoloDevice."""
        self.amp: ArcamSolo = amp
        self.zone = zone
        self.config_entry: ConfigEntry = config_entry
        self.zone_callback_id = None

    async def async_added_to_hass(self) -> None:
        """Handle common setup and zone callback."""
        def callback_update_ha() -> None:
            self.schedule_update_ha_state()

        self._added_to_hass = True
        self.zone_callback_id = self.amp.set_zone_callback(zone=self.zone, callback=callback_update_ha)

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.config_entry.data[CONF_HOST]}:{self.config_entry.data[CONF_PORT]}")},
            name=self.config_entry.data[CONF_NAME],
            model="Solo",
            sw_version=self.amp.software_version,
            manufacturer="Arcam"
        )

    @property
    def available(self) -> bool:
        """Return whether this device is available."""
        return self.amp.available

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        if self.zone not in self.amp.zones:
            return None
        return self.amp.zones.get(self.zone).get("source", None)
