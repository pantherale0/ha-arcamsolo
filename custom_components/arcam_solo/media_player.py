"""Media player entity for Arcam Solo."""

from typing import Any

from pyarcamsolo import ArcamSolo
from pyarcamsolo.commands import SOURCE_SELECTION_CODES

from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNKNOWN, CONF_NAME, CONF_HOST, CONF_PORT
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaPlayerDeviceClass
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

PARALLEL_UPDATES = 0

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
    ):
    """Set up the Arcam Solo media_player."""
    arcam: ArcamSolo = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        ArcamSoloDevice(
            config_entry=config_entry,
            arcam=arcam,
            name=config_entry.data[CONF_NAME],
            dev_unique_id=f"{config_entry.data[CONF_HOST]}:{config_entry.data[CONF_PORT]}"
        )
    ])

class ArcamSoloDevice(MediaPlayerEntity):
    """Represnetation of Arcam Solo device."""

    _attr_should_poll = False
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER

    def __init__(
            self,
            config_entry: ConfigEntry,
            arcam: ArcamSolo,
            name: str,
            dev_unique_id: str,
            zone: int = 1
    ) -> None:
        """Initialize the Arcam Solo."""
        self._config_entry = config_entry
        self._device_unique_id = dev_unique_id
        self._arcam = arcam
        self._attr_name = name
        self._added_to_hass = False
        self._zone = zone

    async def async_added_to_hass(self) -> None:
        """Complete the initialization."""
        def callback_update_ha() -> None:
            self.schedule_update_ha_state()
        self._added_to_hass = True
        self._arcam.set_zone_callback(
            self._zone,
            callback_update_ha
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        name = self._attr_name
        return {
            "identifiers": {(DOMAIN), f"{self._config_entry.entry_id}"},
            "manufacturer": "Arcam",
            "sw_version": self._arcam.software_version,
            "name": name,
            "model": "Solo"
        }

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"{self._config_entry.entry_id}-{self._zone}"

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        state = self._arcam.zones.get(self._zone)
        if state is None:
            return STATE_UNKNOWN
        return MediaPlayerState.OFF if state["power"] == "Standby" else MediaPlayerState.ON

    @property
    def available(self) -> bool:
        """Returns if the device is available."""
        return self._arcam.available and self._zone in self._arcam.zones

    @property
    def volume_level(self) -> float:
        """Volume level between 0 and 1."""
        volume = self._arcam.zones.get(self._zone).get("volume", None)
        max_vol = 72
        return volume / max_vol if (volume and max_vol) else float(0)

    @property
    def is_volume_muted(self) -> bool:
        """Return if volume is muted."""
        return self._arcam.zones.get(self._zone).get("muted", False)

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return supported features for this platform."""
        features = MediaPlayerEntityFeature(0)
        features |= MediaPlayerEntityFeature.TURN_OFF
        features |= MediaPlayerEntityFeature.TURN_ON
        features |= MediaPlayerEntityFeature.VOLUME_MUTE
        features |= MediaPlayerEntityFeature.VOLUME_SET
        features |= MediaPlayerEntityFeature.VOLUME_STEP
        features |= MediaPlayerEntityFeature.SELECT_SOURCE
        return features

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        return self._arcam.zones.get(self._zone).get("source", None)

    @property
    def source_list(self) -> list[str]:
        """Return all available sources."""
        return [
            i[1] for i in SOURCE_SELECTION_CODES.items()
            if i[1] != "N/A"
        ]

    @property
    def media_title(self) -> str:
        """Title of current playing media."""
        return self.source

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return self._arcam.zones.get(self._zone)

    async def async_turn_on(self) -> None:
        """Turn the player on."""
        return await self._arcam.turn_on()

    async def async_turn_off(self) -> None:
        """Turn the player off."""
        return await self._arcam.turn_off()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        return await self._arcam.set_source(source)

    async def async_volume_up(self) -> None:
        """Volume up media player."""
        return await self._arcam.send_ir_command(
            command="volume_plus"
        )

    async def async_volume_down(self) -> None:
        """Volume down media player."""
        return await self._arcam.send_ir_command(
            command="volume_minus"
        )

    async def async_set_volume_level(self, volume) -> None:
        """Set volume level."""
        max_vol = 72
        return await self._arcam.set_volume(
            round(volume*max_vol)
        )

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute media player."""
        if mute:
            return await self._arcam.send_ir_command(
                command="mute_on"
            )
        else:
            return await self._arcam.send_ir_command(
                command="mute_off"
            )
