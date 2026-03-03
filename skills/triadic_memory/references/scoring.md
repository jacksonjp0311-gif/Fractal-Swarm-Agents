# Triadic Memory Scoring Notes

Updated weighting system used by the Triadic Memory Crucible:

- **recency_score**: Derived from entry timestamps (`## HH:MM TZ` headers) when present; falls linearly to 0 over 72h. Falls back to mtime only when timestamps are missing.
- **density_score**: Entry count / 12 (capped at 1) to keep multiscale drift bounded even if the diary grows large.
- **alignment_density**: Weighted phrase scoring (see lexicon below) normalized by token count. Negative phrases subtract from alignment.
- **drift_density**: Weighted phrase scoring for drift/divergence terms normalized by token count.
- **conflict_density**: Tracks explicit negations (“not aligned”, “anti-align”, etc.). Used to reduce alignment density and surface contradictions.
- **pressure_score**: `drift_score * (1 - alignment_score)` — a scalar you can feed into recovery biasing or threshold tightening.
- **hash**: SHA-256 over `(timestamp, content, recorded_at)` per entry to detect tampering or drift across machines (relative paths only).
- **confidence**: 0.15 base + contributions from recency/alignment/density + inverse pressure so noisy diaries reduce trust automatically.

## Lexicon (weights)
```
ALIGNMENT_WEIGHTS = {
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
DRIFT_WEIGHTS = {
  "drift": 1.0,
  "divergence": 0.9,
  "chaos": 0.8,
  "collapse": 0.8,
  "misaligned": 0.7,
  "entropy": 0.6,
  "desync": 0.6,
}
NEGATION_WEIGHTS = {
  "not aligned": 1.0,
  "anti-align": 0.9,
  "out of phase": 0.7,
  "against coherence": 0.8,
}
```
Tune these weights to emphasize the language patterns you care about, then rerun `load_recent_memory()` to propagate the new signals into telemetry.
