"""The Control D integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import async_get_user_data, create_api, is_auth_error
from .const import DOMAIN, PLATFORMS
from .coordinator import ControlDCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


@dataclass(slots=True)
class ControlDRuntimeData:
    """Runtime data for Control D."""

    api: object
    coordinator: ControlDCoordinator


type ControlDConfigEntry = ConfigEntry[ControlDRuntimeData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Control D integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ControlDConfigEntry) -> bool:
    """Set up Control D from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    api = create_api(api_key)

    try:
        await async_get_user_data(hass, api)
    except Exception as err:  # noqa: BLE001
        if is_auth_error(err):
            raise ConfigEntryAuthFailed("Invalid API key") from err
        raise ConfigEntryNotReady from err

    coordinator = ControlDCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = ControlDRuntimeData(api=api, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ControlDConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
