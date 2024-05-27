"""Custom integration to integrate Arcam Solo into Home Assistant."""
from __future__ import annotations

import logging
from asyncio.exceptions import TimeoutError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady

from pyarcamsolo import ArcamSolo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.REMOTE, Platform.NUMBER, Platform.BUTTON]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})
    arcam = ArcamSolo(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT]
    )
    try:
        await arcam.connect()
    except TimeoutError as exc:
        raise ConfigEntryNotReady(exc) from exc
    except Exception as exc:
        raise ConfigEntryError(exc) from exc
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
