# OpenClaw Skill · Triadic Memory Crucible

The Triadic Memory Crucible is a portable OpenClaw skill that turns any operator diary in `%USERPROFILE%\.openclaw\workspace\memory` (or `~/.openclaw/workspace/memory`) into a deterministic telemetry source for the ASTS Control Kernel. It ingests Markdown journals, scores alignment vs. drift using weighted lexicons, hashes every snapshot, and injects `memory_*` metrics directly into `theta`. The repository ships with both a slim bridge bundle and a full ASTS mirror so other operators can adopt or extend the stack without touching your live environment.

## Why it matters
- **Deterministic diary ingestion** – Structured header parsing, timestamp normalization, lexical weighting (alignment, drift, negations), and entry hashing make every snapshot reproducible.
- **Telemetry-ready metrics** – `memory_alignment`, `memory_density`, `memory_recency`, `memory_drift`, and the new `memory_pressure` scalar land in `metrics`, while `theta['memory']` receives the hashed payload for downstream agents.
- **Episodic tiering** – Entries flow through an upgraded fast/slow memory allocator that favors high-alignment, low-drift directives for slow retention and keeps volatile content in the fast lane.
- **Portable skill packaging** – `scripts/asts_memory` contains the entire memory subsystem snapshot, while `engines/asts_control_kernel` mirrors the full repo for staged refactors or upstream contributions.

## Repository layout
```
OpenClaw Skill Triadic Memory Crucible/
├─ README.md                     # Project overview (this file)
├─ SKILL.md                      # Skill frontmatter + operator instructions
├─ GET_STARTED.txt               # Quick deployment checklist
├─ references/
│   └─ scoring.md                # Weighted lexicon + scoring notes
├─ engines/
│   ├─ asts_memory_bridge/       # Minimal bridge helpers (drop-in copy)
│   └─ asts_control_kernel/      # Full ASTS mirror for safe iteration
└─ scripts/
    └─ asts_memory/              # Portable snapshot used during packaging
        ├─ bridge/
        ├─ episodic/
        ├─ runtime/
        ├─ summaries/
        └─ README*.md           # Mini docs per subsystem
```

## How it works
1. **Filesystem → Snapshot**: `memory/bridge/openclaw_workspace.py` scans the operator diary, extracts entries (via `## HH:MM TZ` headers), computes densities, negation penalties, and SHA-256 hashes.
2. **Snapshot → Episodic caches**: `memory/episodic/store.py` seeds fast/slow buffers based on recency, alignment density, and drift volatility.
3. **Observer hook**: `runtime/observers/memory_bridge.py` emits the normalized metrics plus the raw snapshot payload.
4. **Telemetry aggregation**: `runtime/telemetry_field/aggregator.py` merges the metrics, exposes `memory_pressure`, and places the hashed snapshot under `theta['memory']`.
5. **Control loop**: ASTS recovery / monitoring logic can now bias decisions using the live diary signal instead of static configs.

## Getting started
See `GET_STARTED.txt` for a copy-paste checklist. In short:
1. Ensure your diary lives under `%USERPROFILE%\.openclaw\workspace\memory` (default for OpenClaw agents). Set `OPENCLAW_MEMORY_ROOT` if you relocate it.
2. Drop `engines/asts_memory_bridge/*` (or the entire `scripts/asts_memory/*`) into your ASTS repo if you want to replace the stock memory subsystem.
3. Verify the bridge locally:
   ```powershell
   cd <skill-root>
   python - <<'PY'
   import sys
   from pathlib import Path
   sys.path.insert(0, str((Path.cwd() / 'engines' / 'asts_control_kernel').resolve()))
   from memory.bridge.openclaw_workspace import load_recent_memory
   snapshot = load_recent_memory()
   print(snapshot.payload())
   PY
   ```
4. Run ASTS (`PYTHONIOENCODING=utf-8 python main.py`) and watch the telemetry stream for the new `memory_*` metrics.

## Packaging / distribution
To generate a `.skill` bundle from a CLAWBOT checkout:
```powershell
cd C:\Users\jacks\OneDrive\Desktop\CLAWBOT
python skills\skill-creator\scripts\package_skill.py "C:\Users\jacks\OneDrive\Desktop\OpenClaw Skill Triadic Memory Crucible"
```
Distribute the resulting archive or drop this folder into another agent’s `skills/` directory.

## Publish checklist
- [x] Paths sanitized (no user-specific absolute references outside examples)
- [x] `__pycache__` and state artifacts stripped
- [x] Full ASTS mirror included for transparency, but `.git` / `.venv` omitted
- [x] Skill verified against live diary

Need to extend the lexicon, integrate telemetry swarms, or push upstream changes back into ASTS? Fork this repo, update the mirrored files, and package a new skill revision—every iteration should raise the floor on alignment stability.
