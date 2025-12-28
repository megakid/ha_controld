# ControlD Home Assistant Integration (Scaffold)

This repository resets the slate for a future ControlD custom component. The Octopus Intelligent code that previously lived here has been removed, leaving a clean, HACS-ready layout plus tooling to build sensors, switches, or config flows on top of ControlD's API.

## Project status

* ✅ Repository structured for HACS (`custom_components/controld`).
* ✅ `uv`-native Python project for dependency management and tooling.
* ✅ Basic sensors, coordinator, and API client scaffolding.
* ✅ PyCtrlD wired in for authenticated API access (placeholder stats until upstream adds analytics helpers).
* ✅ Pytest + HA harness with placeholder tests.
* ⏳ Implement real ControlD API client, config flow, and entities.

## Quick start

```bash
# Install development dependencies
uv sync --group dev

# Run formatters, linters, types, tests
uv run ruff format --check .
uv run ruff check .
uv run mypy custom_components/controld
uv run pytest -q

# Validate HA config (heads-up: slow but helpful)
uv run python -m homeassistant.scripts.check_config --config ./_tmp_config
```

## Repository layout

```
custom_components/controld/  # Integration stub (manifest, sensors, coordinator)
tests/                      # pytest-homeassistant-custom-component tests
_tmp_config/                # Barebones HA config for schema validation
.github/workflows/          # uv-based CI pipeline
pyproject.toml              # uv project metadata & tooling scripts
hacs.json / info.md         # HACS metadata
```

## Next steps

1. Replace the placeholder stats logic in `custom_components/controld/api.py` with real analytics data once PyCtrlD exposes those endpoints.
2. Build a config flow (`config_flow.py`) to capture credentials in the UI.
3. Flesh out sensors/entities by consuming the coordinator data.
4. Tag releases (`v0.x.y`) so HACS users can install pinned versions; keep `manifest.json["version"]` and `pyproject.toml` in sync.

See `info.md` for the short HACS blurb that appears in the UI.
