from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from core.audit_logger import AuditLogger
from core.identity import derive_agent_id


def _read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def spawn(repo_root: str, parent_id: str, depth: int, cfg: Dict, nonce: Optional[str] = None) -> str:
    """
    Creates runtime directory + writes per-agent config. No process launching yet.
    (Keep launch as an explicit next step once orchestration is stable.)
    """
    root = Path(repo_root).resolve()
    agents_dir = root / cfg.get("agent_dir", "agents")
    agents_dir.mkdir(parents=True, exist_ok=True)

    agent_id = derive_agent_id(parent_id=parent_id, depth=depth, nonce=nonce)
    agent_dir = agents_dir / f"agent-{agent_id}"
    agent_dir.mkdir(parents=True, exist_ok=True)

    # runtime subdirs
    (agent_dir / "memory").mkdir(exist_ok=True)
    (agent_dir / "logs").mkdir(exist_ok=True)
    (agent_dir / "cache").mkdir(exist_ok=True)

    # lock file (presence indicates allocated)
    (agent_dir / "runtime.lock").write_text("locked\n", encoding="utf-8")

    # per-agent config
    agent_cfg = {
        "agent_id": agent_id,
        "parent_id": parent_id,
        "depth": depth,
        "memory_root": str((agent_dir / "memory").resolve()),
        "logs_root": str((agent_dir / "logs").resolve()),
        "cache_root": str((agent_dir / "cache").resolve()),
    }
    _write_json(agent_dir / "config.json", agent_cfg)

    # audit
    alog = AuditLogger(agent_dir, filename=str(cfg.get("audit_event_file", "events.jsonl")))
    alog.emit("AGENT_ALLOCATED", {"agent_id": agent_id, "parent_id": parent_id, "depth": depth})

    return agent_id