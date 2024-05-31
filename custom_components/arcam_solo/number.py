"""Number platform for radio functions."""

from __future__ import annotations


from homeassistant.config_entries import ConfigEntry
from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNKNOWN
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import ServiceValidationError
from pyarcamsolo import ArcamSolo

from .const import DOMAIN, CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES
from .device import ArcamSoloDevice

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Arcam Solo remote."""
    arcam = hass.data[DOMAIN][config_entry.entry_id]
    entities = []
    if "sound_controls" in config_entry.data.get(CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES):
        entities.extend([
                ArcamFrequencyLevelEntity(
                    amp=arcam,
                    config_entry=config_entry,
                    zone=1,
                    level="Bass"
                ),
                ArcamFrequencyLevelEntity(
                    amp=arcam,
                    config_entry=config_entry,
                    zone=1,
                    level="Treble"
                ),
                ArcamFrequencyLevelEntity(
                    amp=arcam,
                    config_entry=config_entry,
                    zone=1,
                    level="Balance"
                )
            ]
        )
    if "display_controls" in config_entry.data.get(CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES):
        entities.extend([
                ArcamDisplayBrightnessEntity(
                    amp=arcam,
                    config_entry=config_entry,
                    zone=1,
                    key="standby_display_brightness",
                    name="Standby Display Brightness",
                    command="stby_display_brightness"
                ),
                ArcamDisplayBrightnessEntity(
                    amp=arcam,
                    config_entry=config_entry,
                    zone=1,
                    key="display_brightness",
                    name="Display Brightness",
                    command="display_brightness"
                )
            ]
        )
    if "radio_controls" in config_entry.data.get(CONF_ENABLED_FEATURES, DEFAULT_CONF_ENABLED_FEATURES):
        entities.append(
            ArcamNumberTunerEntity(
                amp=arcam,
                config_entry=config_entry,
                zone=1 # multi-zone not supported yet
            )
        )
    async_add_entities(entities)

class ArcamFrequencyLevelEntity(ArcamSoloDevice, NumberEntity):
    """Number entity for bass level."""

    _attr_mode = "slider"
    _attr_has_entity_name = True

    def __init__(self, amp: ArcamSolo, config_entry: ConfigEntry, zone: int, level: str) -> None:
        """Initialize the Arcam Solo."""
        self._attr_name = f"{level} Level"
        self._level = level
        if level == "Balance":
            self._attr_native_step = 1
            self._attr_native_max_value = 9
            self._attr_native_min_value = -9
        else:
            self._attr_native_step = 2
            self._attr_native_max_value = 14
            self._attr_native_min_value = -14
            self._attr_native_unit_of_measurement = "dB"
            self._attr_device_class = NumberDeviceClass.SOUND_PRESSURE
        super().__init__(amp, config_entry, zone)

    @property
    def unique_id(self) -> str:
        """Return entity unique ID."""
        return f"{self.config_entry.entry_id}-{self.zone}-number-{self._level.lower()}"

    @property
    def native_value(self) -> float:
        """Return the current value."""
        if self.zone not in self.amp.zones:
            return STATE_UNKNOWN
        return self.amp.zones[self.zone].get(self._level.lower(), STATE_UNKNOWN)

    async def async_set_native_value(self, value: float) -> None:
        """Set a new value for this entity."""
        if value % self._attr_native_step > 0:
            raise ServiceValidationError(f"Only multiples of {self._attr_native_step} are supported for this entity.")
        # apply offset of 100, halve for entities that only support multiples of two.
        value = (value / self._attr_native_step)+100
        await self.amp.send_raw_command(
            command=self._level.lower(),
            data=[
                int(value).to_bytes(byteorder='big', signed=True)
            ]
        )

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

class ArcamNumberTunerEntity(ArcamSoloDevice, NumberEntity):
    """Number entity for tuner frequency."""

    _attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return entity unique ID."""
        return f"{self.config_entry.entry_id}-{self.zone}-number-tuner"

    @property
    def name(self) -> str:
        """Return entity name."""
        return "Radio Frequency"

    @property
    def device_class(self) -> NumberDeviceClass:
        """Return the type of device this is."""
        return NumberDeviceClass.FREQUENCY

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the measurement."""
        if self.source is None:
            return None
        if "AM" in self.source:
            return "kHz"
        if "FM" in self.source:
            return "MHz"
        return None

    @property
    def native_value(self) -> float:
        """Return the current value."""
        if not self.available:
            return STATE_UNKNOWN
        if self.zone not in self.amp.zones:
            return STATE_UNKNOWN
        return self.amp.zones[self.zone].get("radio_frequency", None)

    @property
    def native_max_value(self) -> float:
        """Return max value."""
        if not self.available:
            return 0.0
        if self.source == "AM":
            return 1712.0
        if self.source == "FM":
            return 108.0

    @property
    def native_min_value(self) -> float:
        """Return min value."""
        if not self.available:
            return 0.0
        if self.source == "AM":
            return 522.0
        if self.source =="FM":
            return 88.0

    @property
    def native_step(self) -> float:
        """Return min value."""
        if not self.available:
            return 0.0
        if self.source == "AM":
            return 9
        if self.source == "FM":
            return 0.05

    @property
    def mode(self) -> str:
        """Entity display mode."""
        return "slider"

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return self.source in ["AM", "FM"]

    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes."""
        return {
            "max_value": self.native_max_value,
            "min_value": self.native_min_value,
            "step": self.native_step,
            "frequency": self.native_unit_of_measurement,
            "source": self.source
        }

    # async def async_set_native_value(self, value: float) -> None:
    #     """Set the tuner frequency using stepping."""
    #     while True:
    #         if self.native_value < value:
    #             await self.amp.send_ir_command(
    #                 command="navigate_down"
    #             )
    #         if self.native_value > value:
    #             await self.amp.send_ir_command(
    #                 command="navigate_up"
    #             )
    #         await asyncio.sleep(0.2) # delay to allow updates to come through
    #         if self.native_value == value:
    #             break
    #         if (self.native_value == self.native_max_value
    #             or self.native_value == self.native_min_value):
    #             break # safety

class ArcamDisplayBrightnessEntity(ArcamSoloDevice, NumberEntity):
    """Entity that controls the brightness of the display."""

    _attr_native_max_value = 4
    _attr_native_min_value = 0
    _attr_has_entity_name = True

    def __init__(
            self,
            amp: ArcamSolo,
            config_entry: ConfigEntry,
            zone: int,
            key: str,
            name: str,
            command: str) -> None:
        """Initialize the Arcam Solo."""
        super().__init__(amp, config_entry, zone)
        self._key = key
        self._command = command
        self._attr_name = name

    @property
    def unique_id(self) -> str:
        """Return entity unique ID."""
        return f"{self.config_entry.entry_id}-{self.zone}-number-{self._key}"

    @property
    def available(self) -> bool:
        """Return if the entity is currently available."""
        state = self.amp.zones.get(self.zone)
        if state is None:
            return False
        if "power" not in state:
            return False
        if state["power"] == "Standby" and self._key == "display_brightness":
            return False
        if state["power"] != "Standby" and self._key == "standby_display_brightness":
            return False
        return True

    @property
    def native_value(self) -> float:
        """Return the current value."""
        if self.zone not in self.amp.zones:
            return STATE_UNKNOWN
        return self.amp.zones[self.zone].get(self._key, STATE_UNKNOWN)

    @property
    def icon(self) -> str:
        """Return entity icon."""
        if isinstance(self.native_value, str):
            return "mdi:brightness-1"
        if self.native_value == 0:
            return "mdi:brightness-5"
        if self.native_value >= 1 and self.native_value <= 3:
            return "mdi:brightness-6"
        if self.native_value == 4:
            return "mdi:brightness-7"
        return "mdi:brightness-1"

    async def async_set_native_value(self, value: float) -> None:
        """Set the entity value."""
        await self.amp.send_raw_command(
            command=self._command,
            data=[int(value).to_bytes()]
        )
