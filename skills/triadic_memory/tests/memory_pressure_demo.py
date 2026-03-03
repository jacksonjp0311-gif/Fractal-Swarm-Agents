"""Memory pressure → recovery mode demo.

Run this script to see how drift/pressure combinations influence the
recovery controller without touching your production ASTS checkout.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = ROOT / "engines" / "asts_control_kernel"

sys.path.insert(0, str(ENGINE_ROOT))

from engine.recovery.controller import decide  # type: ignore  # pylint: disable=import-error


def simulate_case(label: str, slow_drift: float, pressure: float) -> None:
    theta = {
        "drift": {"slow": slow_drift, "fast": slow_drift, "total": slow_drift, "per_key": {}},
        "metrics": {"memory_pressure": pressure},
    }
    decision = decide(theta, str(ENGINE_ROOT))
    print(f"{label}: drift_slow={slow_drift:.4f}, pressure={pressure:.4f} -> mode={decision['mode']} actions={decision['actions']}")


if __name__ == "__main__":
    simulate_case("Baseline", slow_drift=0.003, pressure=0.05)
    simulate_case("Warn threshold", slow_drift=0.0065, pressure=0.20)
    simulate_case("Recover with high pressure", slow_drift=0.0105, pressure=0.60)
    simulate_case("Reset candidate", slow_drift=0.0128, pressure=0.85)
