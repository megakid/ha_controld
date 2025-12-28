"""Constants for the Control D integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "ha_controld"

PLATFORMS: list[Platform] = [Platform.SELECT]

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

