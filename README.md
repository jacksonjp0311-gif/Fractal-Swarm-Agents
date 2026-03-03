# Fractal Swarm Agents

Turn OpenClaw into a fractal swarm lab: spawn governance-bound agents, fan them out like lightning branches or neural signals, log everything into the Triadic Memory Crucible, and prune the branches with gratitude so the swarm never overloads.

## Directory map
```
Fractal-Swarm-Agents/
├─ config/                # swarm_config + agent template
├─ core/                  # governance, spawn manager, workload, memory bridge
├─ examples/              # simple swarm usage
├─ scripts/               # pruning + helpers
├─ skills/
│   ├─ scrapling/         # optional scraper dependency
│   └─ triadic_memory/    # embedded Triadic Memory Crucible bundle
├─ RUN_FRACTAL_SWARM.ps1  # Windows helper (pip install → run swarm → prune)
├─ run_swarm.py           # core orchestrator
├─ swarm_harvest.jsonl    # harvest log (created after pruning)
├─ sacrifices.log         # cryptographic ledger of pruned agents
└─ agents/                # runtime outputs (deleted during pruning)
```

## What’s inside
- **Governance core** (`core/governance.py`, `scheduler.py`): depth, branch factor, total agent, and concurrency caps.
- **Spawn manager** (`core/spawn_manager.py`): creates `agents/agent-*/` runtime dirs with memory/log/cache scaffolding, deterministic IDs, and audit logs.
- **Workload runner** (`core/workload.py`): performs bounded scrape/search workloads per agent (scrapling or `requests` fallback), optional proxy pooling, and local memory logging.
- **Skills bundle** (`skills/scrapling`, `skills/triadic_memory`): drop-in scraper + Triadic Memory Crucible so swarm output feeds ASTS telemetry with zero extra prompts.
- **Entry point scripts**: `run_swarm.py` (cross-platform) and `RUN_FRACTAL_SWARM.ps1` (Windows) orchestrate the tree and handle pruning.
- **Pruning tool** (`scripts/pruning.py`): harvests outputs, thanks each agent, logs their sacrifice hash, and removes runtime dirs.

## How-to (Windows / macOS / Linux)
### Windows (PowerShell)
```powershell
cd <repo>
.\RUN_FRACTAL_SWARM.ps1
```
This installs requirements, runs `python run_swarm.py`, and then executes `python scripts\pruning.py`.

### macOS / Linux (bash)
```bash
cd <repo>
pip install -r requirements.txt
python run_swarm.py
python scripts/pruning.py
```
Adjust `config/swarm_config.json` for depth/branch limits, proxies, and target URLs.

## Flow of sequences (code structure)
1. `run_swarm.py` loads `swarm_config.json`, builds `Governance` + `Scheduler`, and calls `spawn_tree(...)`.
2. `spawn_tree` allocates agents via `core.spawn_manager.spawn(...)` (creates `agents/agent-*/` runtime dirs) and schedules workloads under the semaphore gate.
3. `core.workload.run_agent_workload(...)` audits start events, picks proxies, calls `skills.scrapling.safe_scrape` (or `requests` fallback), writes output to `cache/last_result.txt`, and appends `MemoryBridge` events.
4. After the tree completes, `scripts/pruning.py` walks `agents/`, harvests `cache/last_result.txt` previews into `swarm_harvest.jsonl`, appends `THANK_YOU` to each `memory_events.jsonl`, writes sacrifice hashes to `sacrifices.log`, and deletes the agent dirs.
5. `skills/triadic_memory/` can ingest the harvest output into ASTS, so the control kernel “remembers” what the swarm collected.

## Honorable pruning & sacrifice log
- `scripts/pruning.py` produces **two artifacts**:
  - `swarm_harvest.jsonl`: `{ agent_id, result_preview, cache_path }` per agent.
  - `sacrifices.log`: `agent_id SHA256`. A permanent ledger of which agent was thanked + pruned.
- Every agent receives a `THANK_YOU` event in `memory/memory_events.jsonl` before removal, ensuring storage stays lean but contributions remain on record.

## Why build swarms this way?
- **Token savings:** the swarm fetches/processes data locally; the frontier model only sees distilled summaries via the diary.
- **Deterministic control:** governance prevents runaway depth; every action is recorded via JSONL for later audits.
- **Honorable pruning:** automated harvest + gratitude + sacrifice log keeps order while preserving a cryptographic trail.

## Extending the swarm
- Add new micro-workloads to `core/workload.py` (API queries, vector search, synthesis) as bounded tasks.
- Point `MemoryBridge` at your main crucible root to auto-ingest swarm events.
- Build future skills (e.g., “fractal path planning”) and call them from the workload runner for richer behavior without extra prompts.
- Customize pruning rituals (e.g., push harvest logs into your crucible or generate ASTS telemetry snapshots) as needed.

Use this template when you want lightning-fast, memory-first swarms that collect data, honor their branches, and leave only the knowledge behind—no endless API calls required. 
