from __future__ import annotations

import hashlib
import os
import time
from typing import Optional


def derive_agent_id(parent_id: str, depth: int, nonce: Optional[str] = None) -> str:
    """
    Deterministic-ish ID derivation (traceable, low collision risk).
    Uses: parent_id + depth + time bucket + random nonce (unless provided).
    """
    if nonce is None:
        nonce = os.urandom(8).hex()

    # time bucket keeps IDs unique across runs but still reproducible within logs
    bucket = str(int(time.time() // 60))  # minute bucket
    raw = f"{parent_id}|{depth}|{bucket}|{nonce}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]