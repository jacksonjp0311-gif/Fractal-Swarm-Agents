from metrics.drift.drift import compute_drift
from metrics.drift.multiscale import multi_scale
from metrics.divergence.divergence import compute_divergence
from metrics.pressure.pressure import compute_pressure
from invariants.fingerprint.fingerprint import fingerprint
from runtime.telemetry_field.contracts import validate

def aggregate(reports):
    # Merge metrics from observers (last write wins; deterministic by observer order)
    metrics = {}
    memory_payloads = []
    seen_metric_keys = set()
    for r in reports:
        validate(r, seen_metric_keys)
        metrics.update(r.get('metrics', {}))
        seen_metric_keys.update(r.get('metrics', {}).keys())
        if 'memory_snapshot' in r:
            memory_payloads.append(r['memory_snapshot'])

    D_total, per_key = compute_drift(metrics)
    D_ms = multi_scale(D_total)  # persisted state: fast/slow

    V = compute_divergence(reports)
    P = compute_pressure(metrics)

    # Fingerprint over the observable payload (metrics only for now; expand later)
    H = fingerprint(metrics)

    payload = {
        'metrics': metrics,
        'drift': {
            'total': D_total,
            'fast': D_ms.get('fast', 0.0),
            'slow': D_ms.get('slow', 0.0),
            'per_key': per_key
        },
        'divergence': V,
        'pressure': P,
        'hash': H
    }

    if memory_payloads:
        merged = memory_payloads[0] if len(memory_payloads) == 1 else memory_payloads
        payload['memory'] = merged
        if isinstance(merged, dict):
            stats = merged.get('stats', {})
            metrics.setdefault('memory_hash', merged.get('hash'))
            metrics.setdefault('memory_pressure', stats.get('pressure_score'))

    return payload
