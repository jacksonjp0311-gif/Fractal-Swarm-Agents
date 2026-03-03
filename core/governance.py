from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Limits:
    max_depth: int
    max_agents_total: int
    branch_factor: int
    max_concurrent_agents: int


class Governance:
    """
    Central boundary enforcement.
    Tracks total agent count in-process (single run).
    """

    def __init__(self, cfg: Dict) -> None:
        self.limits = Limits(
            max_depth=int(cfg.get("max_depth", 3)),
            max_agents_total=int(cfg.get("max_agents_total", 25)),
            branch_factor=int(cfg.get("branch_factor", 2)),
            max_concurrent_agents=int(cfg.get("max_concurrent_agents", 4)),
        )
        self._agents_created = 0

    @property
    def agents_created(self) -> int:
        return self._agents_created

    def can_spawn(self, depth: int) -> None:
        if depth > self.limits.max_depth:
            raise RuntimeError(f"Governance: depth cap exceeded ({depth} > {self.limits.max_depth})")
        if self._agents_created >= self.limits.max_agents_total:
            raise RuntimeError(f"Governance: total agent cap exceeded ({self._agents_created} >= {self.limits.max_agents_total})")

    def register_spawn(self) -> None:
        self._agents_created += 1