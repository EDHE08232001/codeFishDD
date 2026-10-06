"""Turn raw counts into survival probabilities and save results."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def p0(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    return counts.get("0", 0) / total if total else float("nan")


def p0_curve(all_counts: list[dict[str, int]]) -> np.ndarray:
    return np.array([p0(c) for c in all_counts])


def save_json(path: str | Path, payload: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=lambda o: o.tolist())


if __name__ == "__main__":
    # run from the project root:  python -m src.analysis
    import os
    import tempfile

    assert p0({"0": 750, "1": 250}) == 0.75
    assert p0({"1": 100}) == 0.0
    assert np.isnan(p0({}))

    curve = p0_curve([{"0": 900, "1": 100}, {"0": 600, "1": 400}, {"0": 510, "1": 490}])
    print("P(0) curve:", curve)
    assert np.allclose(curve, [0.9, 0.6, 0.51])

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "sub", "out.json")  # parent folder is created for you
        save_json(path, {"delays_us": np.array([10.0, 20.0]), "p0": {"none": curve}})
        back = json.load(open(path))
        print("round trip:", back)
        assert back["delays_us"] == [10.0, 20.0]
        assert np.allclose(back["p0"]["none"], curve)
    print("analysis.py OK")