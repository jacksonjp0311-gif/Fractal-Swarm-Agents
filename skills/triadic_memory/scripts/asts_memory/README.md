# Memory
This directory contains the memory subsystem scaffolding for episodic and summary behaviors.

## What it does
- Defines extension points for future memory-aware control patterns.
- `bridge/` now syncs the local OpenClaw workspace memory (`~/.openclaw/workspace/memory`) into ASTS.
- `episodic/store.py` seeds fast/slow memory caches from the bridge so observers can report alignment metrics.

## Mini directory
- `bridge/`
- `episodic/`
- `summaries/`

## Notes
- Bridge helpers prefer the `OPENCLAW_MEMORY_ROOT` env var but default to the workspace path when unset.
- Episodic helpers clear/reseed memory buckets on each observer run to keep telemetry deterministic.
