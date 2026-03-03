from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ProxyState:
    proxy: str
    score: float = 0.0
    cooldown_until_ms: int = 0
    fails: int = 0
    oks: int = 0


class ProxyPool:
    """
    Minimal hardening:
    - weighted selection by score
    - cooldown after failures
    """

    def __init__(self, proxies: List[str], cooldown_seconds: int = 90) -> None:
        self.cooldown_ms = int(cooldown_seconds) * 1000
        self._states: Dict[str, ProxyState] = {p: ProxyState(proxy=p) for p in proxies}

    def _now(self) -> int:
        return int(time.time() * 1000)

    def pick(self) -> Optional[str]:
        now = self._now()
        available = [s for s in self._states.values() if s.cooldown_until_ms <= now]
        if not available:
            return None

        # Soft weights: 1 + max(score,0)
        weights = [1.0 + max(s.score, 0.0) for s in available]
        chosen = random.choices(available, weights=weights, k=1)[0]
        return chosen.proxy

    def report_ok(self, proxy: str) -> None:
        s = self._states.get(proxy)
        if not s:
            return
        s.oks += 1
        s.score += 1.0

    def report_fail(self, proxy: str) -> None:
        s = self._states.get(proxy)
        if not s:
            return
        s.fails += 1
        s.score -= 2.0
        s.cooldown_until_ms = self._now() + self.cooldown_ms