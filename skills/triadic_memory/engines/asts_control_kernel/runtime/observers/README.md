# Runtime Observers
This directory contains domain observer implementations.

## What it does
- Produces deterministic observer reports for code/runtime/reasoning/resources/integration domains.
- `memory_bridge.py` ingests workspace memory snapshots to expose alignment/drift metrics to the telemetry field.

## Mini directory
- `code_structure.py`
- `runtime_exec.py`
- `reasoning_quality.py`
- `resources.py`
- `integration.py`
- `memory_bridge.py`
- `base.py`

## Notes
- Observer keys and scales affect drift computation and alert behavior.
- Memory observer depends on `memory/bridge/openclaw_workspace.py`; set `OPENCLAW_MEMORY_ROOT` to override the default path.
