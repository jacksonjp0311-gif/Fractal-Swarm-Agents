from __future__ import annotations

from memory.episodic.store import seed_from_workspace


def observe_memory(env):
    snapshot = seed_from_workspace()

    metrics = {
        "memory_alignment": snapshot.alignment_score,
        "memory_recency": snapshot.recency_score,
        "memory_density": snapshot.density_score,
        "memory_drift": snapshot.drift_score,
        "memory_pressure": snapshot.pressure_score,
    }

    return {
        "domain": "memory",
        "metrics": metrics,
        "confidence": snapshot.confidence,
        "memory_snapshot": snapshot.payload(),
    }
