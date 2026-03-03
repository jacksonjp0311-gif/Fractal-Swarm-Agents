from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "agents"
HARVEST_PATH = ROOT / "swarm_harvest.jsonl"
SACRIFICES_PATH = ROOT / "sacrifices.log"


def iter_agent_dirs() -> Iterator[Path]:
    if not AGENTS_DIR.exists():
        return iter(())
    return (p for p in sorted(AGENTS_DIR.iterdir()) if p.is_dir() and p.name.startswith("agent-"))


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(json.dumps(payload, ensure_ascii=False) + "\n")


def record_sacrifice(agent_dir: Path, agent_id: str) -> None:
    cocktail = (agent_id + str(agent_dir.resolve())).encode("utf-8", errors="ignore")
    sacrifice_hash = hashlib.sha256(cocktail).hexdigest()
    line = f"{agent_id} {sacrifice_hash}\n"
    SACRIFICES_PATH.open("a", encoding="utf-8").write(line)


def thank_agent(memory_dir: Path, agent_id: str) -> None:
    mem_file = memory_dir / "memory_events.jsonl"
    event = {"kind": "THANK_YOU", "agent_id": agent_id}
    append_jsonl(mem_file, event)


def harvest_agent(agent_dir: Path) -> None:
    agent_id = agent_dir.name.replace("agent-", "")
    cache_file = agent_dir / "cache" / "last_result.txt"
    result_preview = None
    if cache_file.exists():
        data = cache_file.read_text(errors="ignore")
        result_preview = data[:2000]
    record = {
        "agent_id": agent_id,
        "result_preview": result_preview,
        "cache_path": str(cache_file) if cache_file.exists() else None,
    }
    append_jsonl(HARVEST_PATH, record)
    thank_agent(agent_dir / "memory", agent_id)
    record_sacrifice(agent_dir, agent_id)
    shutil.rmtree(agent_dir)
    print(f"Harvested and removed {agent_id}")


def main() -> None:
    harvested = False
    for agent_dir in list(iter_agent_dirs()):
        harvest_agent(agent_dir)
        harvested = True
    if harvested:
        print("Harvest complete. See", HARVEST_PATH, "and", SACRIFICES_PATH)
    else:
        print("No agents to prune.")


if __name__ == "__main__":
    main()
