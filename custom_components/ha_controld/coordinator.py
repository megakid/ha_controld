"""DataUpdateCoordinator for Control D."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import async_list_devices, is_auth_error
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class ControlDDevice:
    """Normalized device model for platform code."""

    device_id: str
    name: str
    status: Any
    raw: Any


class ControlDCoordinator(DataUpdateCoordinator[dict[str, ControlDDevice]]):
    """Coordinator for Control D devices."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: Any) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, ControlDDevice]:
        """Fetch data from Control D."""
        try:
            devices = await async_list_devices(self.hass, self.api)
        except Exception as err:  # noqa: BLE001
            if is_auth_error(err):
                # Let setup handle reauth; at runtime we surface as an update failure.
                raise UpdateFailed("Authentication failed") from err
            raise UpdateFailed(str(err)) from err

        data: dict[str, ControlDDevice] = {}
        for dev in devices:
            # pyctrld model has: device_id, name, status
            data[dev.device_id] = ControlDDevice(
                device_id=dev.device_id, name=dev.name, status=dev.status, raw=dev
            )
        return data
