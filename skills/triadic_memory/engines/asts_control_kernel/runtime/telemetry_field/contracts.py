import math
from typing import Dict, Any, Iterable, Set

class ObserverReportError(ValueError):
    """Raised when an observer report violates the schema."""


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not math.isnan(value) and not math.isinf(value)


def validate(report: Dict[str, Any], seen_metrics: Set[str] | None = None) -> None:
    if not isinstance(report, dict):
        raise ObserverReportError("Observer report must be a dict")

    domain = report.get("domain")
    metrics = report.get("metrics")
    confidence = report.get("confidence")

    if not isinstance(domain, str) or not domain.strip():
        raise ObserverReportError("Observer report missing domain name")
    if not isinstance(metrics, dict) or not metrics:
        raise ObserverReportError(f"Observer '{domain}' published empty metrics")
    if not _is_number(confidence):
        raise ObserverReportError(f"Observer '{domain}' confidence must be a finite number")

    metric_names: Iterable[str] = metrics.keys()
    for name in metric_names:
        if not isinstance(name, str) or not name.strip():
            raise ObserverReportError(f"Observer '{domain}' metric keys must be non-empty strings")
        value = metrics[name]
        if not _is_number(value):
            raise ObserverReportError(f"Observer '{domain}' metric '{name}' is not a finite number")

    if seen_metrics is not None:
        collisions = seen_metrics.intersection(metric_names)
        if collisions:
            joined = ", ".join(sorted(collisions))
            raise ObserverReportError(
                f"Observer '{domain}' attempted to overwrite existing metrics: {joined}"
            )
