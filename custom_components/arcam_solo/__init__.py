"""Custom integration to integrate Arcam Solo into Home Assistant."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_DEVICE, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady

from pyarcamsolo import ArcamSolo

from .const import DOMAIN, DEFAULT_CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.REMOTE, Platform.NUMBER, Platform.BUTTON]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    arcam = ArcamSolo(
        uri=entry.data[CONF_DEVICE],
        scan_interval=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_CONF_SCAN_INTERVAL)
    )
    try:
        await arcam.connect()
    except (
        TimeoutError,
        ConnectionAbortedError,
        ConnectionRefusedError,
        ConnectionResetError,
        RuntimeError,
        OSError
    ) as exc:
        if arcam:
            await arcam.shutdown()
            del arcam
        raise ConfigEntryNotReady from exc
    except Exception as exc:
        raise ConfigEntryError from exc
    hass.data[DOMAIN][entry.entry_id] = arcam

    # setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a entry."""
    arcam: ArcamSolo = hass.data[DOMAIN][entry.entry_id]
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await arcam.shutdown()
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    else:
        _LOGGER.warning("unload_entry failed.")
    return unload_ok

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entry to latest version."""
    if entry.version == 1:
        # Uses old aiotelnet library, now replaced with serialx
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_DEVICE: f"socket://{entry.data[CONF_HOST]}:{int(entry.data[CONF_PORT])}"
            },
            version=2
        )
        return True
    return False
