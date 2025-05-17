---
trigger: always_on
---

---
description: >
  Main project memory: guides architecture, modularity, plugin design, and refactoring plan
mode: always
globs:
  - project_root/**/*.py
---

# DebugPlayer Project Memory Context

## Overview

This is a PySide6-based playback tool for analyzing self-driving vehicle logs. The tool is being refactored to support:
- Modular plugin architecture
- Clear data/model interfaces using Pydantic
- Synchronized time-series playback across views
- Visualization panels: trajectory, camera, plots, FSM, events

## 📁 Project Root
The source code resides under `project_root/`, with the following important submodules:

| Folder         | Purpose                                        |
|----------------|------------------------------------------------|
| `core/`        | Timeline, playback controller, core logic     |
| `gui/`         | Qt-based widgets (to be refactored into plugins) |
| `plugins/`     | Location of new dynamically loadable modules  |
| `tests/`       | Unit and integration tests                    |
| `interfaces/`  | Abstract protocols/interfaces between layers  |
| `plots/`       | Static/legacy plot-based visualizations       |
| `utils/`       | Shared utilities                              |

## 🧩 Plugin Framework
All future visualization modules must conform to the `BaseDebugWidget` pattern.

Each plugin module must include:
- `plugin.py` with `register_plugin(bus, data_manager, config=None)`
- `view.py` implementing a `BaseDebugWidget` subclass
- Optional: a `plugin.json` or `plugin_meta.yaml` config for UI-builder compatibility

Plugins are hotloaded from `plugins/`.

## 📐 Widget Guidelines
Refer to rules in `PySide6_Widget_Development.mdc`.

## 📊 Data Loading Rules
Refer to `DataLoader_LogParsing_MVP.mdc`.

## 🔄 Synchronization Strategy
Refer to `DataManager_Synchronization.mdc`.

## 🔬 Refactor Process
1. Add tests for any pre-existing functionality before refactor
2. Gradually convert fixed widgets in `gui/` or `plots/` into plugins
3. Maintain functionality and visual parity after each change

## 🧪 Test Strategy
- Use `pytest`
- Use `mock data snapshots` for visual regression
- Ensure coverage across all widget/plugin types
