from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

_ENTRY_HEADER = re.compile(r"^##\s+(.+)$")
_WORD_SPLIT = re.compile(r"[^a-zA-Z0-9]+")
_DEFAULT_ROOT = os.path.abspath(
    os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "memory")
)

ALIGNMENT_WORDS = ("align", "alignment", "coherence", "coherent")
DRIFT_WORDS = ("drift", "divergence")


@dataclass
class MemoryEntry:
    timestamp: str
    content: str
    source_file: str

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "content": self.content,
            "source_file": self.source_file,
        }


@dataclass
class MemorySnapshot:
    root: str
    entries: List[MemoryEntry] = field(default_factory=list)
    alignment_mentions: int = 0
    drift_mentions: int = 0
    recency_seconds: Optional[float] = None

    @property
    def recency_score(self) -> float:
        if not self.entries or self.recency_seconds is None:
            return 0.0
        horizon = 72 * 3600  # three days
        score = 1.0 - min(self.recency_seconds, horizon) / horizon
        return round(max(0.0, min(1.0, score)), 3)

    @property
    def density_score(self) -> float:
        if not self.entries:
            return 0.0
        return round(min(1.0, len(self.entries) / 12.0), 3)

    @property
    def alignment_score(self) -> float:
        if not self.entries:
            return 0.0
        ratio = self.alignment_mentions / max(1, len(self.entries))
        return round(max(0.0, min(1.0, ratio)), 3)

    @property
    def drift_score(self) -> float:
        if not self.entries:
            return 0.0
        ratio = self.drift_mentions / max(1, len(self.entries))
        return round(max(0.0, min(1.0, ratio)), 3)

    @property
    def confidence(self) -> float:
        base = 0.2
        if self.entries:
            base += 0.3
        base += 0.25 * self.recency_score
        base += 0.25 * self.alignment_score
        return round(max(0.0, min(0.99, base)), 3)

    def payload(self) -> dict:
        return {
            "root": self.root,
            "entries": [e.as_dict() for e in self.entries],
            "stats": {
                "recency_score": self.recency_score,
                "density_score": self.density_score,
                "alignment_score": self.alignment_score,
                "drift_score": self.drift_score,
                "entry_count": len(self.entries),
            },
        }


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


def _parse_entries(path: str) -> List[MemoryEntry]:
    entries: List[MemoryEntry] = []
    current_header: Optional[str] = None
    buffer: List[str] = []

    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            for raw in handle:
                line = raw.strip()
                match = _ENTRY_HEADER.match(line)
                if match:
                    if buffer:
                        entries.append(
                            MemoryEntry(
                                timestamp=current_header or "",
                                content=" ".join(buffer).strip(),
                                source_file=path,
                            )
                        )
                        buffer = []
                    current_header = match.group(1)
                    continue
                if line:
                    buffer.append(line)
    except FileNotFoundError:
        return entries

    if buffer:
        entries.append(
            MemoryEntry(
                timestamp=current_header or "",
                content=" ".join(buffer).strip(),
                source_file=path,
            )
        )

    return entries


def _count_keywords(text: str, keywords: tuple[str, ...]) -> int:
    tokens = _WORD_SPLIT.split(text.lower())
    return sum(1 for token in tokens if token in keywords)


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

    newest_mtime: Optional[float] = None
    for path in files:
        for entry in _parse_entries(path):
            snapshot.entries.append(entry)
            snapshot.alignment_mentions += _count_keywords(entry.content, ALIGNMENT_WORDS)
            snapshot.drift_mentions += _count_keywords(entry.content, DRIFT_WORDS)
            if len(snapshot.entries) >= max_entries:
                break
        if newest_mtime is None or os.path.getmtime(path) > newest_mtime:
            newest_mtime = os.path.getmtime(path)
        if len(snapshot.entries) >= max_entries:
            break

    if newest_mtime is not None:
        snapshot.recency_seconds = max(0.0, (datetime.now(timezone.utc).timestamp() - newest_mtime))

    return snapshot
