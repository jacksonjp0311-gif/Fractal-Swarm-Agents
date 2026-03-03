from __future__ import annotations

from typing import List

from memory.bridge.openclaw_workspace import MemoryEntry, MemorySnapshot, load_recent_memory

memory_fast: List[MemoryEntry] = []
memory_slow: List[MemoryEntry] = []


def add_episode(entry: MemoryEntry, slow: bool = False) -> None:
    memory_fast.append(entry)
    if slow:
        memory_slow.append(entry)


def _is_slow_candidate(entry: MemoryEntry) -> bool:
    age_hours = (entry.age_seconds or 0.0) / 3600.0 if entry.age_seconds is not None else None
    strong_alignment = entry.alignment_density >= 0.6 and entry.drift_density <= 0.35
    volatile = entry.drift_density >= 0.6 and entry.alignment_density < 0.4

    if strong_alignment:
        return True
    if volatile:
        return False

    if age_hours is not None:
        if age_hours >= 24:
            return True
        if age_hours <= 6 and entry.drift_density > entry.alignment_density:
            return False

    return entry.alignment_density >= entry.drift_density


def seed_from_workspace(max_files: int = 5, max_entries: int = 12) -> MemorySnapshot:
    snapshot = load_recent_memory(max_files=max_files, max_entries=max_entries)
    if snapshot.entries:
        memory_fast.clear()
        memory_slow.clear()
        for entry in snapshot.entries:
            add_episode(entry, slow=_is_slow_candidate(entry))
    return snapshot
