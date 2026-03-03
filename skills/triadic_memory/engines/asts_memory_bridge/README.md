# ASTS Memory Bridge Engine Copy

This folder mirrors the runtime code that lives in `ASTS-Control-Kernel/memory/bridge/` so the skill stays self-contained even if the main repository moves or is offline.

## Contents
- `__init__.py` – re-exports the helper symbols so imports stay identical to the ASTS layout.
- `openclaw_workspace.py` – filesystem crawler, scoring logic, and snapshot dataclasses that power the `runtime.observers.memory_bridge` observer.

## Why this copy exists
- Skills can now load/inspect/patch the bridge implementation directly without touching the ASTS repo.
- When relocating the OpenClaw workspace or spinning up a clean environment, drop this folder back into `ASTS-Control-Kernel/memory/bridge/` to restore the engine behavior verbatim.

Canonical source: `engines/asts_control_kernel/memory/bridge/`. This folder mirrors that code for portability—do not edit here unless you are deliberately diverging.
