"""Media player entity for Arcam Solo."""

from typing import Any

from pyarcamsolo import ArcamSolo
from pyarcamsolo.commands import SOURCE_SELECTION_CODES

from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNKNOWN, CONF_NAME
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaPlayerDeviceClass,
    MediaType,
    RepeatMode,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import datetime
from .const import DOMAIN
from .device import ArcamSoloDevice

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Arcam Solo media_player."""
    arcam: ArcamSolo = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            ArcamMediaEntity(
                amp=arcam,
                config_entry=config_entry,
                zone=1 # multi-zone not supported yet
            )
        ]
    )


class ArcamMediaEntity(ArcamSoloDevice, MediaPlayerEntity):
    """Represnetation of Arcam Solo media player entity."""

    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_has_entity_name = True
    _attr_name = None # https://developers.home-assistant.io/docs/core/entity#entity-naming

    # def __init__(
    #     self,
    #     config_entry: ConfigEntry,
    #     arcam: ArcamSolo,
    #     name: str,
    #     dev_unique_id: str,
    #     zone: int = 1,
    # ) -> None:
    #     """Initialize the Arcam Solo."""
    #     self._config_entry = config_entry
    #     self._device_unique_id = dev_unique_id
    #     self._arcam = arcam
    #     self._attr_name = name
    #     self._added_to_hass = False
    #     self._zone = zone

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"{self.config_entry.entry_id}-{self.zone}-media_player"

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        state = self.amp.zones.get(self.zone)
        if state is None:
            return STATE_UNKNOWN
        if "power" not in state:
            return STATE_UNKNOWN
        if state["power"] == "Standby":
            return MediaPlayerState.OFF
        if self.source == "CD":
            if state.get("cd_playback_state", None) == "Paused":
                return MediaPlayerState.PAUSED
            if state.get("cd_playback_state", None) == "Loading":
                return MediaPlayerState.BUFFERING
            if state.get("cd_playback_state", None) == "Stopped":
                return MediaPlayerState.IDLE
            if state.get("cd_playback_state", None) == "Playing":
                return MediaPlayerState.PLAYING
            if state.get("cd_playback_state", None) == "Scanning Back":
                return MediaPlayerState.BUFFERING
            if state.get("cd_playback_state", None) == "Scanning Forward":
                return MediaPlayerState.BUFFERING
            if state.get("cd_playback_state", None) == "Tray Open / Empty":
                return MediaPlayerState.ON
            if state.get("cd_playback_state", None) == "Track Skipping":
                return MediaPlayerState.BUFFERING

        return MediaPlayerState.ON

    @property
    def available(self) -> bool:
        """Returns if the device is available."""
        return self.amp.available and self.zone in self.amp.zones

    @property
    def volume_level(self) -> float:
        """Volume level between 0 and 1."""
        volume = self.amp.zones.get(self.zone).get("volume", None)
        max_vol = 72
        return volume / max_vol if (volume and max_vol) else float(0)

    @property
    def is_volume_muted(self) -> bool:
        """Return if volume is muted."""
        return self.amp.zones.get(self.zone).get("muted", False)

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
        if self.source in ("CD", "USB"):
            features |= MediaPlayerEntityFeature.PLAY
            features |= MediaPlayerEntityFeature.PAUSE
            features |= MediaPlayerEntityFeature.STOP
            features |= MediaPlayerEntityFeature.SEEK
            features |= MediaPlayerEntityFeature.REPEAT_SET
            features |= MediaPlayerEntityFeature.SHUFFLE_SET
        if self.source in ("CD", "USB", "DAB", "FM", "AM"):
            features |= MediaPlayerEntityFeature.NEXT_TRACK
            features |= MediaPlayerEntityFeature.PREVIOUS_TRACK
        return features

    @property
    def source_list(self) -> list[str]:
        """Return all available sources."""
        return [i[1] for i in SOURCE_SELECTION_CODES.items() if i[1] != "N/A"]

    @property
    def media_title(self) -> str:
        """Title of current playing media."""
        if self.source == "DAB":
            return self.amp.zones[self.zone].get("radio_station", None)
        if self.source in ("CD", "USB"):
            if self.amp.zones[self.zone].get("cd_playback_state", None) in (
                "Playing",
                "Paused",
            ):
                return f"Track {self.media_track} / {self.media_total_tracks}"
            return self.amp.zones[self.zone].get("cd_playback_state", self.source)
        return self.source

    @property
    def media_position(self) -> int | None:
        """Position of media currently playing in seconds."""
        if self.source in ("CD", "USB"):
            return self.amp.zones[self.zone].get("current_track_position", None)
        return None

    @property
    def media_position_updated_at(self) -> datetime | None:
        """Return the time the media position was updated."""
        if self.source in ("CD", "USB"):
            return datetime.now()
        return None

    @property
    def media_track(self) -> int | None:
        """Return the current track."""
        if self.source in ("CD", "USB"):
            return self.amp.zones[self.zone].get("lsb_current_track", None)
        return None

    @property
    def media_total_tracks(self) -> int | None:
        """Return the total number of tracks."""
        if self.source in ("CD", "USB"):
            return self.amp.zones[self.zone].get("lsb_total_track", None)
        return None

    @property
    def media_duration(self) -> int | None:
        """Total duration of media currently playing in seconds."""
        return None  # TODO

    @property
    def repeat(self) -> RepeatMode:
        """Return current repeat mode."""
        if self.source not in ("CD", "USB"):
            return None
        val = self.amp.zones[self.zone].get("repeat", None)
        if val == "all":
            return RepeatMode.ALL
        if val == "single":
            return RepeatMode.ONE
        return RepeatMode.OFF

    @property
    def shuffle(self) -> bool:
        """Return shuffle mode."""
        if self.source in ("CD", "USB"):
            return self.amp.zones[self.zone].get("shuffle", False)
        return None

    @property
    def media_type(self) -> MediaType | str | None:
        """Return the current media type."""
        if self.source not in ("CD", "USB", "DAB", "FM", "AM"):
            return None
        if self.source in ("DAB", "FM", "AM"):
            return MediaType.MUSIC

        if (
            self.state == MediaPlayerState.PLAYING
            or self.state == MediaPlayerState.PAUSED
            or self.state == MediaPlayerState.BUFFERING
        ):
            return MediaType.MUSIC

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return self.amp.zones.get(self.zone)

    async def async_turn_on(self) -> None:
        """Turn the player on."""
        return await self.amp.turn_on()

    async def async_turn_off(self) -> None:
        """Turn the player off."""
        return await self.amp.turn_off()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        return await self.amp.set_source(source)

    async def async_volume_up(self) -> None:
        """Volume up media player."""
        return await self.amp.send_ir_command(command="volume_plus")

    async def async_volume_down(self) -> None:
        """Volume down media player."""
        return await self.amp.send_ir_command(command="volume_minus")

    async def async_set_volume_level(self, volume) -> None:
        """Set volume level."""
        max_vol = 72
        return await self.amp.set_volume(round(volume * max_vol))

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute media player."""
        if mute:
            return await self.amp.send_ir_command(command="mute_on")
        else:
            return await self.amp.send_ir_command(command="mute_off")

    async def async_media_play(self) -> None:
        """Send play command."""
        if self.source not in ("CD", "USB"):
            raise ServiceValidationError("Current source does not support this action")
        return await self.amp.send_ir_command(command="cd_play")

    async def async_media_pause(self) -> None:
        """Send pause command."""
        if self.source not in ("CD", "USB"):
            raise ServiceValidationError("Current source does not support this action")
        return await self.amp.send_ir_command(command="cd_pause")

    async def async_media_stop(self) -> None:
        """Send stop command."""
        if self.source not in ("CD", "USB"):
            raise ServiceValidationError("Current source does not support this action")
        return await self.amp.send_ir_command(command="cd_stop")

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        if self.source not in ("CD", "USB", "DAB", "AM", "FM"):
            raise ServiceValidationError("Current source does not support this action")
        if self.source in ("DAB", "AM", "FM"):
            return await self.amp.send_ir_command(command="navigate_down")
        return await self.amp.send_ir_command(command="cd_track_previous")

    async def async_media_next_track(self) -> None:
        """Send previous track command."""
        if self.source not in ("CD", "USB", "DAB", "AM", "FM"):
            raise ServiceValidationError("Current source does not support this action")
        if self.source in ("DAB", "AM", "FM"):
            return await self.amp.send_ir_command(command="navigate_up")
        return await self.amp.send_ir_command(command="cd_track_next")

    async def async_set_repeat(self, repeat: RepeatMode) -> None:
        """Set repeat mode."""
        if repeat == RepeatMode.ALL:
            return await self.amp.send_ir_command(
                command="cd_repeat_all"
            )
        if repeat == RepeatMode.ONE:
            return await self.amp.send_ir_command(
                command="cd_repeat_single"
            )
        if repeat == RepeatMode.OFF:
            return await self.amp.send_ir_command(
                command="cd_repeat_off"
            )

    async def async_set_shuffle(self, shuffle: bool) -> None:
        """Set shuffle mode."""
        if shuffle:
            return await self.amp.send_ir_command(
                command="cd_shuffle_on"
            )
        else:
            return await self.amp.send_ir_command(
                command="cd_shuffle_off"
            )
