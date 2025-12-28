"""Control D API helpers.

The upstream `pyctrld` library is synchronous, so all I/O must be executed in the
executor to avoid blocking the Home Assistant event loop.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from pyctrld import ControlDApi, DeviceStatus

_AUTH_ERROR_RE = re.compile(r"HTTP Status:\s*(401|403)\b")


def _pyctrld() -> Any:
    """Import pyctrld lazily.

    This allows the integration to be discovered (and shown in the UI) even
    before requirements are installed.
    """
    import pyctrld  # noqa: PLC0415

    return pyctrld


def create_api(token: str) -> Any:
    """Create a pyctrld API client."""
    return _pyctrld().ControlDApi(token=token)


def is_auth_error(err: BaseException) -> bool:
    """Return True if the exception looks like an auth error."""
    try:
        api_error = _pyctrld()._core.exceptions.ApiError
    except Exception:  # noqa: BLE001
        api_error = None

    if api_error is not None and isinstance(err, api_error):
        return bool(_AUTH_ERROR_RE.search(str(err)))
    return bool(_AUTH_ERROR_RE.search(str(err)))


async def async_get_user_data(hass: HomeAssistant, api: Any) -> Any:
    """Fetch account user data."""
    return await hass.async_add_executor_job(api.account.user_data)


async def async_list_devices(hass: HomeAssistant, api: Any) -> list[Any]:
    """Fetch all devices."""
    return await hass.async_add_executor_job(api.devices.list_all_devices)


async def async_set_device_status(
    hass: HomeAssistant, api: Any, device_id: str, status: Any
) -> None:
    """Set the status of a device."""
    form_data = _pyctrld().ModifyDeviceFormData(status=status)
    await hass.async_add_executor_job(api.devices.modify_device, device_id, form_data)
