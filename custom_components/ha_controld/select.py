"""Select platform for Control D."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ControlDConfigEntry
from .api import _pyctrld, async_set_device_status
from .const import DOMAIN
from .coordinator import ControlDCoordinator, ControlDDevice

PARALLEL_UPDATES = 0

OPTION_ENABLED = "Enabled"
OPTION_SOFT_DISABLED = "Soft Disabled"
OPTION_HARD_DISABLED = "Hard Disabled"

_STATUS_TO_OPTION = {
    # Map pyctrld status -> HA select option label
    "ACTIVE": OPTION_ENABLED,
    "SOFT_DISABLED": OPTION_SOFT_DISABLED,
    "HARD_DISABLED": OPTION_HARD_DISABLED,
}

_OPTION_TO_STATUS = {
    OPTION_ENABLED: "ACTIVE",
    OPTION_SOFT_DISABLED: "SOFT_DISABLED",
    OPTION_HARD_DISABLED: "HARD_DISABLED",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ControlDConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Control D selects based on a config entry."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        ControlDDeviceStatusSelect(entry, coordinator, device.device_id)
        for device in coordinator.data.values()
    )


class ControlDDeviceStatusSelect(
    CoordinatorEntity[ControlDCoordinator],
    SelectEntity,
):
    """Select that sets the enabled/disabled status of a Control D device."""

    _attr_translation_key = "device_status"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_options = [OPTION_ENABLED, OPTION_SOFT_DISABLED, OPTION_HARD_DISABLED]

    def __init__(
        self,
        entry: ControlDConfigEntry,
        coordinator: ControlDCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self._entry = entry
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_device_status"
        self._update_from_device()

    @property
    def _device(self) -> ControlDDevice | None:
        """Return the latest device data."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._device_id)

    def _update_from_device(self) -> None:
        """Update attributes from the latest coordinator data."""
        device = self._device
        if device is None:
            return

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.device_id)},
            name=device.name,
            manufacturer="Control D",
        )

        # pyctrld uses an enum; we compare by enum name to be robust
        status_name = getattr(device.status, "name", None)
        if status_name is None:
            self._attr_current_option = None
            return

        self._attr_current_option = _STATUS_TO_OPTION.get(status_name)

    @property
    def available(self) -> bool:
        """Return True if the entity is available."""
        return self._device is not None and super().available

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_from_device()
        super()._handle_coordinator_update()

    async def async_select_option(self, option: str) -> None:
        """Select a new option."""
        status_name = _OPTION_TO_STATUS.get(option)
        if status_name is None:
            return

        device_status = _pyctrld().DeviceStatus
        await async_set_device_status(
            self.hass,
            self._entry.runtime_data.api,
            self._device_id,
            getattr(device_status, status_name),
        )
        self._attr_current_option = option
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

