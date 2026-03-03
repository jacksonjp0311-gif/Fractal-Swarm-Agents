from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Optional

from core.audit_logger import AuditLogger
from core.memory_bridge import MemoryBridge
from core.proxy_pool import ProxyPool


def _sleep_jitter(base_ms: int = 200) -> None:
    # micro-jitter to avoid synchronous bursts
    import random
    time.sleep((base_ms + random.randint(0, 200)) / 1000.0)


def run_agent_workload(
    repo_root: Path,
    agent_dir: Path,
    cfg: Dict,
    url: str,
    instructions: str = "Fetch page HTML (bounded).",
) -> None:
    """
    Executes one bounded unit of work for an agent:
    - pick proxy (if configured)
    - call safe_scrape wrapper (if present)
    - audit events
    - write result into agent cache
    - record memory event (local JSONL)
    """
    audit = AuditLogger(agent_dir, filename=str(cfg.get("audit_event_file", "events.jsonl")))
    mem = MemoryBridge(agent_dir / "memory")

    # load proxies if present in global cfg (optional)
    proxies = cfg.get("proxies", [])
    pool = ProxyPool(proxies, cooldown_seconds=int(cfg.get("proxy_cooldown_seconds", 90))) if proxies else None

    audit.emit("WORK_START", {"url": url})
    mem.record_event("WORK_START", {"url": url})

    _sleep_jitter(150)

    proxy = pool.pick() if pool else None
    audit.emit("PROXY_PICK", {"proxy": proxy})

    # Attempt to use skills.scrapling.safe_scrape.safe_scrape if it exists
    ok = False
    result_text: Optional[str] = None
    err: Optional[str] = None

    try:
        from skills.scrapling.safe_scrape import safe_scrape  # type: ignore
        audit.emit("SCRAPE_START", {"proxy": proxy})
        try:
            result_text = safe_scrape(url, instructions=instructions, proxy=proxy)
        except TypeError:
            result_text = safe_scrape(url, instructions=instructions)
        ok = True
        if pool and proxy:
            pool.report_ok(proxy)
        audit.emit("SCRAPE_OK", {"bytes": len(result_text) if result_text else 0})
    except Exception:
        # Fallback to requests when scrapling is unavailable
        try:
            import requests
            audit.emit("SCRAPE_FALLBACK", {"method": "requests"})
            resp = requests.get(url, timeout=cfg.get("requests_timeout", 15))
            resp.raise_for_status()
            result_text = resp.text
            ok = True
            audit.emit("REQUESTS_OK", {"status": resp.status_code, "bytes": len(result_text)})
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            if pool and proxy:
                pool.report_fail(proxy)
            audit.emit("SCRAPE_FAIL", {"error": err})

    # persist output (bounded)
    cache_dir = agent_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    out_path = cache_dir / "last_result.txt"

    if ok and result_text is not None:
        # truncate to keep sane disk growth
        max_bytes = int(cfg.get("max_result_bytes", 250_000))
        data = result_text.encode("utf-8", errors="ignore")[:max_bytes]
        out_path.write_bytes(data)
        mem.record_event("SCRAPE_OK", {"bytes": len(data), "path": str(out_path)})
    else:
        out_path.write_text(err or "unknown error", encoding="utf-8")
        mem.record_event("SCRAPE_FAIL", {"error": err or "unknown error"})

    audit.emit("WORK_END", {"ok": ok, "out": str(out_path)})