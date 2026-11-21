"""Re-evaluate route objectives and distribution shifts against pinned primary code."""
import argparse
import csv
import hashlib
import importlib.util
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent
PIN = "ea643183cd45389eefb7fef70d8833efe30a5891"
RUN_SHA256 = "c44ba87f4de8ab7d3d3801e68bbc6c144f621c628819be326eee68c71604168e"


def load_benchmark(repo):
    path = repo / "run.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != RUN_SHA256:
        raise ValueError(f"Expected run.py from commit {PIN}")
    spec = importlib.util.spec_from_file_location("foothold_benchmark", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write(name, rows):
    with (OUT / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def study(repo):
    bench = load_benchmark(repo)
    n = 1400
    x, left, right, rng = bench.terrain(9508, n, True)
    clearance = np.minimum(x-left, right-x) - bench.FOOT
    rng.uniform(-8, 8, (n, 1, 1))  # preserve shared-shift draw order of primary script
    local = rng.uniform(-8, 8, (n, bench.STEPS, 2))
    inward_l = rng.uniform(0, 6, (n, bench.STEPS, 2))
    inward_r = rng.uniform(0, 6, (n, bench.STEPS, 2))
    layout = np.arange(n)[:,None]
    step = np.arange(bench.STEPS)
    widest_path, widest_ok, _ = bench.max_clearance(x, clearance)
    worst = clearance[layout, step, widest_path].min(axis=1)
    rows, paired = [], []
    for scale in (1., 1.25, 1.50, 1.75):
        true_left = left + scale*np.repeat(local+inward_l, 3, axis=2)
        true_right = right + scale*np.repeat(local-inward_r, 3, axis=2)
        supported = np.minimum(x-true_left, true_right-x) >= bench.FOOT
        _, oracle, _ = bench.search(x, supported)
        for margin in sorted({8., 14., 14.*scale}):
            travel, accept, _ = bench.search(x, clearance >= margin)
            wide_accept = widest_ok & (worst >= margin)
            assert np.array_equal(accept, wide_accept)
            by_policy = []
            for name, path in (("travel", travel), ("widest", widest_path)):
                valid = supported[layout, step, path].all(axis=1) & accept
                if margin >= 14.*scale:
                    assert np.array_equal(accept, valid)
                by_policy.append(valid)
                rows.append(dict(scale=scale, geometric_bound_mm=14.*scale, margin_mm=margin, policy=name,
                    layouts=n, feasible=int(oracle.sum()), accepted=int(accept.sum()), valid=int(valid.sum()),
                    invalid=int((accept & ~valid).sum()), rejected_feasible=int((~accept & oracle).sum())))
            valid_travel, valid_widest = by_policy
            score = valid_widest.astype(int) - valid_travel.astype(int)
            delta = score.mean()
            se = score.std(ddof=1) / np.sqrt(n)
            paired.append(dict(scale=scale, margin_mm=margin, layouts=n, accepted=int(accept.sum()),
                widest_only=int((valid_widest & ~valid_travel).sum()), travel_only=int((valid_travel & ~valid_widest).sum()),
                delta_all_layouts=delta, paired_mc_se=se, lower_approx_95=delta-1.96*se, upper_approx_95=delta+1.96*se))
    write("stress.csv", rows)
    write("paired.csv", paired)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("repo", type=Path, help="Local checkout of VEDANT1602/foothold-margin-planning")
    study(p.parse_args().repo)
