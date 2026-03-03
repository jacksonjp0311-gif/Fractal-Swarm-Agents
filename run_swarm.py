from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Dict

from core.governance import Governance
from core.scheduler import Scheduler
from core.spawn_manager import spawn
from core.workload import run_agent_workload


def load_cfg(root: Path) -> Dict:
    cfg_path = root / "config" / "swarm_config.json"
    return json.loads(cfg_path.read_text(encoding="utf-8-sig"))


async def spawn_tree(root: Path, gov: Governance, sched: Scheduler, parent_id: str, depth: int, cfg: Dict) -> None:
    gov.can_spawn(depth)
    gov.register_spawn()

    async with sched.slot():
        agent_id = spawn(str(root), parent_id=parent_id, depth=depth, cfg=cfg)
        print(f"Spawned {agent_id} (depth={depth}, parent={parent_id})")

        # run one bounded workload per agent (safe, local)
        agent_dir = (root / cfg.get("agent_dir", "agents") / f"agent-{agent_id}")
        url = cfg.get("demo_url", "https://example.com/")
        run_agent_workload(root, agent_dir, cfg, url=url)

    if depth >= gov.limits.max_depth:
        return
    if gov.agents_created >= gov.limits.max_agents_total:
        return

    tasks = []
    for _ in range(gov.limits.branch_factor):
        if gov.agents_created >= gov.limits.max_agents_total:
            break
        try:
            gov.can_spawn(depth + 1)
        except RuntimeError:
            break
        tasks.append(spawn_tree(root, gov, sched, parent_id=agent_id, depth=depth + 1, cfg=cfg))

    if tasks:
        await asyncio.gather(*tasks)


def main() -> None:
    root = Path(__file__).resolve().parent
    cfg = load_cfg(root)

    gov = Governance(cfg)
    sched = Scheduler(gov.limits.max_concurrent_agents)

    asyncio.run(spawn_tree(root, gov, sched, parent_id="root", depth=0, cfg=cfg))
    print(f"Done. agents_created={gov.agents_created}")


if __name__ == "__main__":
    main()