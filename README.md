# ControlD Home Assistant Integration

Home Assistant custom integration for [Control D](https://controld.com/) DNS service.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

## Installation

1. Add repository to HACS (see [Custom Repositories](https://hacs.xyz/docs/faq/custom_repositories)) - use `https://github.com/megakid/ha_controld` as the repository URL
2. Install the `ha_controld` integration inside HACS
3. Restart Home Assistant
4. Add the ControlD integration via **Settings → Devices & Services → Add Integration**

## Configuration

You need an API key from your [Control D dashboard](https://controld.com/dashboard).

During setup, enter your API key. The integration will detect all devices configured in your Control D account.

## Entities

For each Control D device, the integration creates:

### Status (Select)

Controls the device status with these options:

- **Enabled** - DNS filtering active
- **Soft Disabled** - Filtering paused (device continues to use Control D DNS)
- **Hard Disabled** - Filtering completely disabled

## Requirements

- Home Assistant 2025.12.0 or newer
- [pyctrld](https://pypi.org/project/pyctrld/) (installed automatically)
