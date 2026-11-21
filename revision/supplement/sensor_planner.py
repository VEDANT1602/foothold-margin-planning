"""One-dimensional foothold planning with a published lateral edge precision model."""

import argparse
import csv
from pathlib import Path
from statistics import NormalDist
import numpy as np
from sensitivity import load_benchmark

HERE = Path(__file__).resolve().parent
NORMAL = NormalDist()


def interval(fails, n):
    if not n:
        return ("", "")
    z = NORMAL.inv_cdf(0.975)
    p = fails / n
    half = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5
    return (
        (p + z * z / (2 * n) - half) / (1 + z * z / n),
        (p + z * z / (2 * n) + half) / (1 + z * z / n),
    )


def experiment(module, wide):
    n, seed = (1400, 8508) if wide else (1400, 9508)
    x, l, r, _ = module.terrain(seed, n, not wide)
    left_room = x - l - module.FOOT
    right_room = r - x - module.FOOT
    free = np.minimum(left_room, right_room)
    depth = np.linspace(0.75, 2.5, 6)
    std = (0.8 + 0.035 * 30 / (90 - 30)) * depth * 1000 / 585
    rng = np.random.default_rng(21908 if wide else 21909)
    random_l, rnd_r = (rng.standard_normal((n, 6, 2)) for i in range(2))
    sign = rng.choice([-1.0, 1.0], size=(n, 1, 1))
    shape = (1, 6, 1)
    local_l = std.reshape(shape) * random_l
    local_r = std.reshape(shape) * rnd_r
    rows = []
    z = NORMAL.inv_cdf(1 - 0.05 / 12)
    for drift in [0, 25]:
        lerr = (local_l + sign * drift).repeat(3, axis=2)
        rerr = (local_r - sign * drift).repeat(3, axis=2)
        fits = (left_room >= lerr) & (right_room >= rerr)
        _, oracle, _ = module.search(x, fits)
        for name, margin in (
            ("travel_0", np.zeros(6)),
            ("travel_8", np.full(6, 8)),
            ("travel_14", np.full(6, 14)),
            ("widest_8", np.full(6, 8)),
            ("chance_5pct", z * std),
            ("chance_plus_25", z * std + 25),
        ):
            if name == "widest_8":
                path, accept, _ = module.max_clearance(x, free)
                accept &= (
                    free[np.arange(n)[:, None], np.arange(6), path].min(axis=1) >= 8
                )
            else:
                path, accept, _ = module.search(x, free >= margin.reshape(shape))
            valid = fits[np.arange(n)[:, None], np.arange(6), path].all(axis=1) & accept
            fails = int((accept & ~valid).sum())
            count = int(accept.sum())
            lo, hi = interval(fails, count)
            paths = x[np.arange(n)[:, None], np.arange(6), path]
            travel = np.abs(np.diff(paths, axis=1, prepend=0)).sum(axis=1)
            rows.append(
                dict(
                    split="wide" if wide else "bottleneck",
                    seed=seed,
                    shared_signed_drift_mm=drift,
                    policy=name,
                    layouts=n,
                    feasible=int(oracle.sum()),
                    accepted=count,
                    valid=int(valid.sum()),
                    invalid=fails,
                    feasible_rejected=int((~accept & oracle).sum()),
                    conditional_failure=fails / count if count else "",
                    wilson95_low=lo,
                    wilson95_high=hi,
                    mean_lateral_travel_mm=travel[accept].mean() if count else "",
                    first_margin_mm=margin[0],
                    last_margin_mm=margin[-1],
                )
            )
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "repository",
        type=Path,
        help="Exact foothold-margin-planning checkout specified in README",
    )
    bench = load_benchmark(p.parse_args().repository)
    rows = experiment(bench, False) + experiment(bench, True)
    assert all(d["accepted"] == d["valid"] + d["invalid"] for d in rows)
    with (HERE / "chance_results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
