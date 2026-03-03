---
name: openclaw-fractal-swarm
description: Portable swarm orchestrator that spawns governance-bound agents in a fractal tree, logs every action, and streams results into the Triadic Memory Crucible. Use this skill to run bounded scrape/search workloads while minimizing API token usage.
---

# OpenClaw Skill · Fractal Swarm Agents

## Overview
This skill wraps a self-contained swarm orchestration stack:
- Governance limits (max depth, total agents, branch factor, concurrency)
- Deterministic agent spawn + identity derivation
- Per-agent runtime scaffolding (`memory/`, `logs/`, `cache/`, audit JSONL)
- Bounded workload runner (optional proxy cycling + `skills.scrapling` integration)
- Memory bridge hooks that emit local JSONL events and can hand off to the Triadic Memory Crucible

It lets you fan out “lightning-style” agents (think fractal tree / brain signal) without touching the frontier model repeatedly—spawn once, let the swarm gather data, and feed summaries back into the diary.

## Quick Start
1. **Install requirements & run helper script:**
   ```powershell
   cd <skill root>
   .\RUN_FRACTAL_SWARM.ps1
   ```
   (Script installs deps, runs `python run_swarm.py`, then prunes via `python scripts\pruning.py`.)
2. **Customize `config/swarm_config.json`:** depth, total agents, concurrency, proxy list, target URL (`demo_url`).
3. **Integrate with Triadic Memory:** copy the `skills/triadic_memory/` bundle (already included) into your OpenClaw setup or point the swarm’s `memory_bridge` at your crucible root via config.

## Architecture snapshot
```
fractal-swarm-agents/
├─ config/               # Governance + agent template JSON
├─ core/                 # Governance, scheduler, spawn manager, workload, memory bridge
├─ skills/
│   ├─ scrapling/        # Web-fetch skill dependency (optional)
│   └─ triadic_memory/   # Embedded Triadic Memory Crucible bundle
├─ run_swarm.py          # Main entrypoint
└─ agents/               # Runtime data (ignored in skill package)
```

## Telemetry & memory integration
Each agent writes:
- `logs/events.jsonl` via `AuditLogger`
- `memory/memory_events.jsonl` via `MemoryBridge`
- `cache/last_result.txt` for bounded output

If you attach the Triadic Memory Crucible, these events can be lifted into ASTS telemetry (`memory_alignment`, `memory_pressure`, etc.) after the swarm run.

## Bounded workloads & token savings
- Swarm uses local scripts (`skills.scrapling.safe_scrape`) to fetch or analyze targets.
- API model is only invoked for orchestration/decision steps, not repeated for each fetch.
- Results stream into memory logs, reducing repeated prompt context and making the entire run reproducible.

## Maintenance tasks
- Update `swarm_config.json` for new topologies (branch factor, depth, demo URLs).
- Extend `core/workload.py` with new micro-tasks (search, API queries, etc.) while keeping them bounded.
- Wire `MemoryBridge` to your crucible root if you want direct diary ingestion.
- Use `examples/simple_swarm.py` as a minimal reference for custom flows.
