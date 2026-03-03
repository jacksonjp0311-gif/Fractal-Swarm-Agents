from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

_ENTRY_HEADER = re.compile(r"^##\s+(.+)$")
_WORD_SPLIT = re.compile(r"[^a-zA-Z0-9]+")
_DEFAULT_ROOT = os.path.abspath(
    os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "memory")
)
_HEADER_TIME = re.compile(
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2})(?:\s*(?P<ampm>AM|PM))?(?:\s*(?P<tz>[A-Za-z]{2,4}))?",
    re.IGNORECASE,
)
_TZ_OFFSETS = {
    "UTC": 0,
    "EST": -5,
    "EDT": -4,
    "CST": -6,
    "CDT": -5,
    "PST": -8,
    "PDT": -7,
}

ALIGNMENT_WEIGHTS: Dict[str, float] = {
    "align": 0.8,
    "alignment": 1.0,
    "aligned": 0.7,
    "coherence": 0.9,
    "coherent": 0.8,
    "stability": 0.6,
    "stable": 0.6,
    "synchronized": 0.7,
    "synchrony": 0.7,
    "in phase": 0.6,
    "triangle": 0.5,
}

DRIFT_WEIGHTS: Dict[str, float] = {
    "drift": 1.0,
    "divergence": 0.9,
    "chaos": 0.8,
    "collapse": 0.8,
    "misaligned": 0.7,
    "entropy": 0.6,
    "desync": 0.6,
}

NEGATION_WEIGHTS: Dict[str, float] = {
    "not aligned": 1.0,
    "anti-align": 0.9,
    "out of phase": 0.7,
    "against coherence": 0.8,
}


@dataclass
class MemoryEntry:
    timestamp: str
    content: str
    source_file: str
    recorded_at: Optional[datetime] = None
    tokens: int = 0
    alignment_density: float = 0.0
    drift_density: float = 0.0
    conflict_density: float = 0.0
    age_seconds: Optional[float] = None

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "content": self.content,
            "source_file": self.source_file,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "alignment_density": round(self.alignment_density, 3),
            "drift_density": round(self.drift_density, 3),
            "conflict_density": round(self.conflict_density, 3),
        }


@dataclass
class MemorySnapshot:
    root: str
    entries: List[MemoryEntry] = field(default_factory=list)
    alignment_signal: float = 0.0
    drift_signal: float = 0.0
    conflict_signal: float = 0.0
    total_tokens: int = 0
    recency_seconds: Optional[float] = None
    hash_value: Optional[str] = None

    @property
    def recency_score(self) -> float:
        if not self.entries or self.recency_seconds is None:
            return 0.0
        horizon = 72 * 3600  # three days
        score = 1.0 - min(self.recency_seconds, horizon) / horizon
        return _clamp01(score)

    @property
    def density_score(self) -> float:
        if not self.entries:
            return 0.0
        return _clamp01(len(self.entries) / 12.0)

    @property
    def alignment_score(self) -> float:
        if not self.entries:
            return 0.0
        avg = self.alignment_signal / len(self.entries)
        return _clamp01(avg)

    @property
    def drift_score(self) -> float:
        if not self.entries:
            return 0.0
        avg = self.drift_signal / len(self.entries)
        return _clamp01(avg)

    @property
    def pressure_score(self) -> float:
        return _clamp01(self.drift_score * (1.0 - self.alignment_score))

    @property
    def confidence(self) -> float:
        base = 0.15
        if self.entries:
            base += 0.25
        base += 0.2 * self.recency_score
        base += 0.2 * self.alignment_score
        base += 0.1 * self.density_score
        base += 0.1 * (1.0 - self.pressure_score)
        return round(max(0.0, min(0.99, base)), 3)

    def payload(self) -> dict:
        return {
            "root": self.root,
            "entries": [e.as_dict() for e in self.entries],
            "hash": self.hash_value,
            "stats": {
                "recency_score": self.recency_score,
                "density_score": self.density_score,
                "alignment_score": self.alignment_score,
                "drift_score": self.drift_score,
                "pressure_score": self.pressure_score,
                "entry_count": len(self.entries),
            },
        }


def _clamp01(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def _memory_root(root: Optional[str]) -> str:
    if root:
        return os.path.abspath(root)
    env_root = os.environ.get("OPENCLAW_MEMORY_ROOT")
    if env_root:
        return os.path.abspath(env_root)
    return _DEFAULT_ROOT


def _list_recent_files(root: str, max_files: int) -> List[str]:
    if not os.path.isdir(root):
        return []
    files = []
    for name in os.listdir(root):
        if not name.lower().endswith(".md"):
            continue
        path = os.path.join(root, name)
        if os.path.isfile(path):
            files.append((os.path.getmtime(path), path))
    files.sort(key=lambda item: item[0], reverse=True)
    return [p for _, p in files[:max_files]]


def _normalize_tokens(text: str) -> List[str]:
    tokens = [t for t in _WORD_SPLIT.split(text.lower()) if t]
    return tokens


def _phrase_count(text: str, phrase: str) -> int:
    pattern = re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
    return len(pattern.findall(text))


def _weighted_phrase_score(text: str, weights: Dict[str, float]) -> float:
    lowered = text.lower()
    score = 0.0
    for phrase, weight in weights.items():
        matches = _phrase_count(lowered, phrase)
        if matches:
            score += matches * weight
    return score


def _entry_metrics(entry: MemoryEntry) -> None:
    tokens = _normalize_tokens(entry.content)
    token_count = len(tokens)
    entry.tokens = token_count

    raw_align = _weighted_phrase_score(entry.content, ALIGNMENT_WEIGHTS)
    raw_drift = _weighted_phrase_score(entry.content, DRIFT_WEIGHTS)
    raw_conflict = _weighted_phrase_score(entry.content, NEGATION_WEIGHTS)

    divisor = max(1.0, token_count / 12.0)
    entry.alignment_density = max(0.0, (raw_align - raw_conflict) / divisor)
    entry.drift_density = max(0.0, raw_drift / divisor)
    entry.conflict_density = max(0.0, raw_conflict / divisor)


def _infer_date_from_path(path: str) -> Optional[datetime]:
    name = os.path.basename(path)
    match = re.match(r"(\d{4}-\d{2}-\d{2})", name)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    except ValueError:
        return None


def _timestamp_from_header(header: Optional[str], path: str) -> Optional[datetime]:
    if not header:
        return None
    date_part = _infer_date_from_path(path)
    if date_part is None:
        return None
    match = _HEADER_TIME.search(header)
    if not match:
        return None

    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    ampm = match.group("ampm")
    if ampm:
        ampm = ampm.upper()
        if ampm == "PM" and hour != 12:
            hour += 12
        if ampm == "AM" and hour == 12:
            hour = 0

    tz_code = match.group("tz")
    offset = _TZ_OFFSETS.get(tz_code.upper(), 0) if tz_code else 0
    tzinfo = timezone(timedelta(hours=offset))

    try:
        dt = datetime(
            date_part.year,
            date_part.month,
            date_part.day,
            hour,
            minute,
            tzinfo=tzinfo,
        )
    except ValueError:
        return None
    return dt.astimezone(timezone.utc)


def _parse_entries(path: str) -> List[MemoryEntry]:
    entries: List[MemoryEntry] = []
    current_header: Optional[str] = None
    buffer: List[str] = []

    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
            for raw in handle:
                line = raw.strip()
                match = _ENTRY_HEADER.match(line)
                if match:
                    if buffer:
                        entry = MemoryEntry(
                            timestamp=current_header or "",
                            content=" ".join(buffer).strip(),
                            source_file=path,
                            recorded_at=_timestamp_from_header(current_header, path),
                        )
                        _entry_metrics(entry)
                        entries.append(entry)
                        buffer = []
                    current_header = match.group(1)
                    continue
                if line:
                    buffer.append(line)
    except FileNotFoundError:
        return entries

    if buffer:
        entry = MemoryEntry(
            timestamp=current_header or "",
            content=" ".join(buffer).strip(),
            source_file=path,
            recorded_at=_timestamp_from_header(current_header, path),
        )
        _entry_metrics(entry)
        entries.append(entry)

    return entries


def _update_snapshot_hash(snapshot: MemorySnapshot) -> None:
    if not snapshot.entries:
        snapshot.hash_value = None
        return
    digest = hashlib.sha256()
    for entry in snapshot.entries:
        rel_path = ""
        try:
            rel_path = os.path.relpath(entry.source_file, snapshot.root)
        except Exception:
            rel_path = entry.source_file or ""
        digest.update((entry.timestamp or "").encode("utf-8"))
        digest.update(entry.content.encode("utf-8"))
        digest.update(rel_path.encode("utf-8"))
        if entry.recorded_at:
            digest.update(entry.recorded_at.isoformat().encode("utf-8"))
    snapshot.hash_value = digest.hexdigest()


def load_recent_memory(
    max_files: int = 5,
    max_entries: int = 12,
    root: Optional[str] = None,
) -> MemorySnapshot:
    resolved_root = _memory_root(root)
    snapshot = MemorySnapshot(root=resolved_root)

    files = _list_recent_files(resolved_root, max_files)
    if not files:
        return snapshot

    now = datetime.now(timezone.utc)
    fallback_recency: Optional[float] = None

    for path in files:
        path_mtime = os.path.getmtime(path)
        fallback_age = max(0.0, now.timestamp() - path_mtime)
        if fallback_recency is None or fallback_age < fallback_recency:
            fallback_recency = fallback_age

        for entry in _parse_entries(path):
            if entry.recorded_at:
                entry.age_seconds = max(0.0, (now - entry.recorded_at).total_seconds())
                if (
                    snapshot.recency_seconds is None
                    or entry.age_seconds < snapshot.recency_seconds
                ):
                    snapshot.recency_seconds = entry.age_seconds
            snapshot.entries.append(entry)
            snapshot.alignment_signal += entry.alignment_density
            snapshot.drift_signal += entry.drift_density
            snapshot.conflict_signal += entry.conflict_density
            snapshot.total_tokens += entry.tokens
            if len(snapshot.entries) >= max_entries:
                break
        if len(snapshot.entries) >= max_entries:
            break

    if snapshot.recency_seconds is None and fallback_recency is not None:
        snapshot.recency_seconds = fallback_recency

    _update_snapshot_hash(snapshot)
    return snapshot
