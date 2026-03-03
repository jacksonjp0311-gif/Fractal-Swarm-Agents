---
name: openclaw-triadic-memory-crucible
description: Portable OpenClaw skill that ingests the operator diary (`%USERPROFILE%\.openclaw\workspace\memory`) and feeds weighted alignment/drift/pressure metrics + hashed snapshots into ASTS telemetry. Use whenever you need deterministic memory ingestion, episodic gating, or diary-driven control biasing.
---

# OpenClaw Skill · Triadic Memory Crucible

## Overview
The crucible links ASTS's `memory/` package directly to the human-authored OpenClaw diary (default: `%USERPROFILE%\\.openclaw\\workspace\\memory`). Each cycle it:
- Parses `## HH:MM TZ` headers, normalizes timestamps, and hashes the snapshot.
- Computes weighted lexical densities for alignment vs drift (with negation penalties) plus a `memory_pressure = drift * (1 - alignment)` scalar.
- Seeds fast/slow episodic caches based on recency + signal quality.
- Emits metrics + payloads that land in `theta['metrics']` and `theta['memory']`.

## Quick Start
1. **Set the path (optional):** Override the default diary path with `setx OPENCLAW_MEMORY_ROOT "D:\memories"` (or use `$env:OPENCLAW_MEMORY_ROOT="..."` for the current shell) before running ASTS if the workspace moved.
2. **Inspect the snapshot:**
   ```powershell
   cd <ASTS_CONTROL_KERNEL_ROOT>
   python - <<'PY'
   from pprint import pprint
   from memory.bridge.openclaw_workspace import load_recent_memory
   snapshot = load_recent_memory()
   pprint(snapshot.payload())
   PY
   ```
   _Replace `<ASTS_CONTROL_KERNEL_ROOT>` with the path to your ASTS Control Kernel checkout._

   - `entries` → ordered list of `timestamp`, `content`, `source_file` tuples pulled from the newest diary files.
   - `stats` → normalized scores that become `memory_alignment`, `memory_recency`, `memory_density`, and `memory_drift` in telemetry metrics.
3. **Update the diary:** Append structured notes (e.g., `## 04:19 EST`) to `memory/YYYY-MM-DD.md` and rerun the observer (or the snippet above) to refresh the scores.

## Telemetry + Observer Integration
1. `memory/bridge/openclaw_workspace.py`: handles filesystem discovery, parsing, keyword scoring, and converts results into a deterministic payload.
2. `memory/episodic/store.py:seed_from_workspace`: clears/represents fast & slow episodic caches from the snapshot every observer run.
3. `runtime/observers/memory_bridge.py`:
   - calls `seed_from_workspace()`
   - emits normalized metrics + confidence for the telemetry aggregator
   - attaches the structured payload under `memory_snapshot`
4. `runtime/telemetry_field/aggregator.py`: merges observer metrics and, when a snapshot is present, stores it under `theta['memory']` so monitoring/recovery/ledger layers can consume the raw human memory stream.

Use GitNexus (`npx gitnexus context ...`) to cite these relationships whenever you discuss structure:
- Observer wiring: `Function:runtime/observers/memory_bridge.py:observe_memory`
- Store seeding: `Function:memory/episodic/store.py:seed_from_workspace`
- Filesystem bridge: `Function:memory/bridge/openclaw_workspace.py:load_recent_memory`
- Telemetry integration: `Function:runtime/telemetry_field/aggregator.py:aggregate`

### Engine Mirror (Skill-local copy)
- The entire `memory/bridge` package is mirrored under `engines/asts_memory_bridge/` inside this skill.
- Drop those files back into `ASTS-Control-Kernel/memory/bridge/` (or import directly via `skills.workspace-memory-bridge.engines.asts_memory_bridge`) if the main repo is unavailable.
- See `engines/asts_memory_bridge/README.md` for provenance and update notes.

### Full Memory Package Snapshot
- `scripts/asts_memory/` contains a straight copy of `ASTS-Control-Kernel/memory/` (episodic, summaries, bridge) so the skill can operate with zero external dependencies.
- README_SKILL_COPY.md inside that folder records the source path/date. Sync it again whenever the upstream memory package changes.

## Maintenance Tasks
- **Audit scoring:** See [`references/scoring.md`](references/scoring.md) for the normalization heuristics used in telemetry. Adjust keyword lists or scoring curves inside `memory/bridge/openclaw_workspace.py` when new directives appear frequently.
- **Extend payloads:** Add extra derived stats (e.g., tag counts) by updating `MemorySnapshot.payload()` and consume them downstream via `theta['memory']['stats']`.
- **Backfill diary entries:** When handed raw instructions (chat logs, voice notes), convert them into dated Markdown files before running the control kernel so the observer has signal to work with.
- **Testing:** Run the snippet from *Quick Start* or execute `PYTHONIOENCODING=utf-8 python main.py` to confirm the observer, aggregator, and ledger flows ingest the updated memory stream without unicode/logging issues.
