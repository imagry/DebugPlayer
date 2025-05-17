# 🔧 Phase 1: Refactor & Stabilize DebugPlayer

## 🎯 Objective
Begin a structured test-first refactor of the existing DebugPlayer PySide6 project to improve test coverage, isolate core logic, and prepare for future plugin modularization.

This phase focuses on:
- Identifying key modules and existing coupling issues
- Writing unit + integration tests for the current logic
- Improving modularity of playback and data-handling code
- Ensuring all work maintains compatibility with the current main interface

## 📁 Project Structure
Codebase is located in `project_root/`, including:
- `core/`: Playback engine, timeline, logic
- `gui/`: QWidget implementations (to be refactored later)
- `tests/`: Place all new tests here using `pytest`
- `plugins/`: Will be activated in Phase 3

## 🧠 Memory Rules to Use
@project
@DataLoader_LogParsing_MVP
@DataManager_Synchronization

## 🔬 Tasks to Begin With

1. Analyze existing code in `project_root/core/` and `project_root/gui/`
2. Scaffold unit tests for:
   - Timeline playback engine
   - DataManager synchronization
   - Existing FSM handling (if testable)
3. Add integration test: loading and scrubbing a log timeline
4. Document gaps in test coverage and design contracts/interfaces where missing
5. Refactor only if you can verify functionality is unchanged via tests

## 🧪 Testing
Use `pytest`, and prefer readable tests over clever ones. For GUI-dependent code, consider smoke tests only for now.

## 🧩 Plugin System
Do NOT implement plugins yet. Just improve separation and prepare for a future plugin loader by modularizing interfaces where necessary.

## 💡 Output Expectations
- Test coverage report or estimate
- Refactored functions or modules (only if test-covered)
- Notes or todos where further separation is recommended
