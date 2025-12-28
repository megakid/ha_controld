"""Config flow for the Control D integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY

from .api import async_get_user_data, create_api, is_auth_error
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


class ControlDConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Control D."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            api = create_api(api_key)
            try:
                user = await async_get_user_data(self.hass, api)
            except Exception as err:  # noqa: BLE001
                if is_auth_error(err):
                    errors["base"] = "invalid_api_key"
                else:
                    _LOGGER.debug("Error communicating with Control D: %s", err)
                    errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user.PK)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user.email, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=AUTH_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Dialog that informs the user that reauth is required."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            api = create_api(api_key)
            try:
                user = await async_get_user_data(self.hass, api)
            except Exception as err:  # noqa: BLE001
                if is_auth_error(err):
                    errors["base"] = "invalid_api_key"
                else:
                    errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user.PK)
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry, data_updates=user_input
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=AUTH_SCHEMA,
            errors=errors,
        )

