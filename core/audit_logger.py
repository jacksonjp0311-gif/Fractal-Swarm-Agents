from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


def now_ms() -> int:
    return int(time.time() * 1000)


def write_event_jsonl(path: Path, event: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, ensure_ascii=False)
    path.open("a", encoding="utf-8").write(line + "\n")


class AuditLogger:
    """
    JSONL audit logger.
    Writes minimal, truth-only events suitable for replay/debug.
    """

    def __init__(self, agent_runtime_dir: Path, filename: str = "events.jsonl") -> None:
        self.path = agent_runtime_dir / filename

    def emit(self, kind: str, payload: Optional[Dict[str, Any]] = None) -> None:
        evt: Dict[str, Any] = {
            "t_ms": now_ms(),
            "kind": kind,
        }
        if payload:
            evt.update(payload)
        write_event_jsonl(self.path, evt)