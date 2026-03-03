from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional


class MemoryBridge:
    """
    Optional bridge to Triadic Memory Crucible.
    This module must NOT hard-fail if Crucible isn't present.
    """

    def __init__(self, agent_memory_root: Path) -> None:
        self.root = agent_memory_root

    def record_event(self, kind: str, payload: Dict[str, Any]) -> None:
        """
        Minimal, safe default: append JSONL locally inside agent memory.
        If Crucible APIs exist later, this becomes an adapter.
        """
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "memory_events.jsonl"
        import json, time
        evt = {"t_ms": int(time.time()*1000), "kind": kind, **payload}
        path.open("a", encoding="utf-8").write(json.dumps(evt, ensure_ascii=False) + "\n")