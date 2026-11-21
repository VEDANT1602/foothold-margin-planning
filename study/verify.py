"""Independently check routing optimality and recompute every released tally."""

import csv
import heapq
from collections import defaultdict
from pathlib import Path
import numpy as np
from terrain_routes import ROWS, OFFSETS, FEET, NX, NZ, plan

HERE = Path(__file__).resolve().parent


def objective(columns, nominal):
    offsets = columns - (nominal + FEET)
    return int(np.abs(offsets).sum() + np.abs(np.diff(offsets)).sum())


def heap_search(mask, nominal):
    # Admissible heuristic: the final foot-row center offset has to return to zero.
    center = len(OFFSETS) // 2
    if not mask[ROWS[0], nominal + FEET[0]]:
        return None
    queue = [(0, 0, 0, center)]
    seen = set()
    while queue:
        _, cost, row, col = heapq.heappop(queue)
        if (row, col) in seen:
            continue
        seen.add((row, col))
        if row == len(ROWS) - 1:
            if col == center:
                return cost
            continue
        for j in range(max(col - 2, 0), min(col + 3, len(OFFSETS))):
            x = nominal + FEET[row + 1] + OFFSETS[j]
            if (row + 1, j) in seen or not mask[ROWS[row + 1], x]:
                continue
            partial = cost + abs(col - j) + abs(OFFSETS[j])
            heapq.heappush(queue, (partial + abs(OFFSETS[j]), partial, row + 1, j))
    return None


rng = np.random.default_rng(194)
for prob in [0.4, 0.65, 0.9, 1.0]:
    for _ in range(100):
        mask = rng.random((NZ, NX)) < prob
        nominal = NX // 2
        path = plan(mask, nominal, False)
        np.testing.assert_equal(
            None if path is None else objective(path[1], nominal), heap_search(mask, nominal)
        )

buckets = defaultdict(list)
with (HERE / "routes.csv").open() as f:
    for r in csv.DictReader(f):
        key = (r["cells_required"], r["roughness_m"], r["policy"])
        buckets[key].append(r)
with (HERE / "scene_metrics.csv").open() as f:
    scenes = list(csv.DictReader(f))
assert len(scenes) == 194 and [
    int(x["scene"]) for x in scenes if int(x["frame_valid"]) == 0
] == [30]
assert len(buckets) == 36
with (HERE / "summary.csv").open() as f:
    for entry in csv.DictReader(f):
        rows = buckets[tuple(entry[c] for c in ["cells_required", "roughness_m", "policy"])]
        assert len(rows) == int(entry["queries"]) == 965
        assert len({(r["scene"], r["lane_cell"]) for r in rows}) == 965
        for outcome in [
            "accepted",
            "reference_feasible",
            "validated",
            "contradicted",
            "unresolved",
            "strict_confirmed",
            "strict_contradicted",
            "strict_unresolved",
        ]:
            assert int(entry[outcome]) == sum(int(row[outcome]) for row in rows)
        assert int(entry["rejected_reference_feasible"]) == sum(
            r["accepted"] == "0" and r["reference_feasible"] == "1" for r in rows
        )
        for row in rows:
            for keys in [
                ("validated", "contradicted", "unresolved"),
                ("strict_confirmed", "strict_contradicted", "strict_unresolved"),
            ]:
                assert sum(int(row[k]) for k in keys) == int(row["accepted"])
            assert int(row["validated"]) <= int(row["reference_feasible"])
print(
    "All 36 cohort summaries, 34,740 decisions, and 400 independent optimal-search comparisons passed."
)
