"""Evaluate a fixed-heading foot-placement lattice on calibrated KITTI 2012 scenes."""

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
from functools import partial
from pathlib import Path
import zipfile
import cv2
import numpy as np
from scipy.ndimage import maximum_filter, minimum_filter, distance_transform_edt, convolve

STEP = 0.10
XMIN, ZMIN = -4.5, 6.0
NX, NZ = 90, 90
LANES = np.array([-26, -13, 0, 13, 26])
ROWS = 10 + 4 * np.arange(15)
OFFSETS = np.arange(-8, 9)
FEET = np.where(np.arange(len(ROWS)) % 2 == 0, -2, 2)


def points(disp, projection, right):
    row, col = np.nonzero(disp > 0)
    focal = projection[0, 0]
    z = -right[0, 3] / disp[row, col]
    valid = (z >= 5) & (z <= 19)
    z, row, col = z[valid], row[valid], col[valid]
    return np.column_stack(
        (
            (col - projection[0, 2]) * z / focal,
            (row - projection[1, 2]) * z / projection[1, 1],
            z,
        )
    )


def ground_frame(p):
    # Estimate the road frame solely from the presumed camera-height band in stereo.
    x, y, z = p.T
    select = (abs(x) < 2.5) & (z >= 6) & (z <= 16) & (y > 0.9) & (y < 2.3)
    if select.sum() < 300:
        return None
    a = np.column_stack([np.ones(select.sum()), x[select], z[select] - 10])[::4]
    heights = y[select][::4]
    coef = np.array([np.median(heights), 0.0, 0.0])
    for _ in range(7):
        weight = np.sqrt(np.minimum(1.0, 0.08 / np.maximum(abs(heights - a @ coef), 1e-8)))
        coef = np.linalg.lstsq(a * weight[:, None], heights * weight, rcond=None)[0]
    if abs(coef[1]) > 0.35 or abs(coef[2]) > 0.35:
        return None
    up = np.array([coef[1], -1.0, coef[2]])
    up /= np.linalg.norm(up)
    ahead = np.array([0.0, 0.0, 1.0]) - up[2] * up
    ahead /= np.linalg.norm(ahead)
    axes = np.column_stack([np.cross(ahead, up), up, ahead])
    return np.array([0.0, coef[0] - 10 * coef[2], 0.0]), axes


def binned(p, frame):
    x, h, z = ((p - frame[0]) @ frame[1]).T
    xi = np.floor((x - XMIN) / STEP).astype(int)
    zi = np.floor((z - ZMIN) / STEP).astype(int)
    ok = (xi >= 0) & (xi < NX) & (zi >= 0) & (zi < NZ)
    ix = zi[ok] * NX + xi[ok]
    heights = h[ok]
    result = np.full(NZ * NX, np.nan)
    order = np.lexsort((heights, ix))
    ix, heights = ix[order], heights[order]
    ids, start, count = np.unique(ix, return_index=True, return_counts=True)
    enough = count >= 2
    lo = start + (count - 1) // 2
    hi = start + count // 2
    result[ids[enough]] = (heights[lo[enough]] + heights[hi[enough]]) / 2
    return result.reshape(NZ, NX)


def footprint(h, rough, min_cells):
    # A coverage rule specifies how many of the nine heights must be observed.
    count = convolve(
        np.isfinite(h).astype("uint8"), np.ones((3, 3), dtype="uint8"), mode="constant", cval=0
    )
    observed = count >= min_cells
    top = maximum_filter(np.where(np.isfinite(h), h, -np.inf), size=3)
    bottom = minimum_filter(np.where(np.isfinite(h), h, np.inf), size=3)
    valid = observed & (top - bottom <= rough) & (top <= 0.40) & (bottom >= -0.40)
    return observed, valid


def plan(safe, nominal, greedy):
    look = nominal + OFFSETS[None, :] + FEET[:, None]
    available = safe[ROWS[:, None], look]
    available[0, OFFSETS != 0] = False
    available[-1, OFFSETS != 0] = False
    center = len(OFFSETS) // 2
    if not available[0, center]:
        return None
    if greedy:
        step = center
        path = [step]
        for mask in available[1:]:
            cand = np.flatnonzero(mask & (abs(np.arange(len(mask)) - step) <= 2))
            if not len(cand):
                return None
            step = min(cand, key=lambda c: (abs(OFFSETS[c]), abs(c - step), c))
            path.append(step)
    else:
        cost = np.full(len(OFFSETS), np.inf)
        cost[center] = 0
        after = []
        for mask in available[1:]:
            new = np.full_like(cost, np.inf)
            parent = np.full(len(cost), -1)
            for j in np.flatnonzero(mask):
                left = max(0, j - 2)
                right = min(len(cost), j + 3)
                indices = np.arange(left, right)
                options = cost[left:right] + abs(indices - j)
                best = np.argmin(options)
                new[j] = options[best] + abs(OFFSETS[j])
                parent[j] = indices[best]
            cost = new
            after.append(parent)
        if not np.isfinite(cost[center]):
            return None
        path = [center]
        for parent in reversed(after):
            path.append(parent[path[-1]])
        path.reverse()
    return ROWS, look[np.arange(len(ROWS)), path]


def read_png(z, name):
    return cv2.imdecode(np.frombuffer(z.read(name), dtype=np.uint8), cv2.IMREAD_UNCHANGED)


def scene(number, data, calibration):
    cv2.setNumThreads(1)
    with zipfile.ZipFile(data) as z, zipfile.ZipFile(calibration) as cal:
        paths = [
            "training/" + s + f"/{number:06d}_10.png"
            for s in ["image_0", "image_1", "disp_noc"]
        ]
        left, right, truth = (read_png(z, p) for p in paths)
        lines = cal.read(f"training/calib/{number:06d}.txt").decode().splitlines()
    projections = [np.fromstring(s.split(":")[1], sep=" ").reshape(3, 4) for s in lines[:2]]
    matcher = cv2.StereoSGBM_create(
        minDisparity=0,
        numDisparities=96,
        blockSize=5,
        P1=8 * 25,
        P2=32 * 25,
        disp12MaxDiff=1,
        preFilterCap=31,
        uniquenessRatio=10,
        speckleWindowSize=50,
        speckleRange=2,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
    )
    pred = points(matcher.compute(left, right).astype(float) / 16, *projections)
    ref = points(truth.astype(float) / 256, *projections)
    frame = ground_frame(pred)
    quality = {
        "scene": number,
        "frame_valid": int(frame is not None),
        "common_cells": 0,
        "median_abs_height_mm": "",
        "p90_abs_height_mm": "",
    }
    routes = []
    if frame is None:
        return quality, routes
    predicted, reference = binned(pred, frame), binned(ref, frame)
    common = np.isfinite(predicted) & np.isfinite(reference)
    if common.any():
        error = np.abs(predicted[common] - reference[common]) * 1000
        quality.update(
            common_cells=int(common.sum()),
            median_abs_height_mm=np.median(error),
            p90_abs_height_mm=np.quantile(error, 0.9),
        )
    for coverage in [5, 7, 9]:
        for threshold in [0.06, 0.10, 0.15]:
            _, safe = footprint(predicted, threshold, coverage)
            observed, ref_safe = footprint(reference, threshold, coverage)
            strict_observed, strict_safe = footprint(reference, threshold, 9)
            distance = distance_transform_edt(np.pad(safe, 1))[1:-1, 1:-1]
            for lane in LANES:
                nominal = NX // 2 + lane
                oracle = plan(ref_safe, nominal, False)
                for mode, greedy, margin in [
                    ("local", True, 0),
                    ("graph", False, 0),
                    ("graph_10cm", False, 1),
                    ("graph_20cm", False, 2),
                ]:
                    path = plan(safe & (distance > margin), nominal, greedy)
                    row = {
                        "scene": number,
                        "cells_required": coverage,
                        "roughness_m": threshold,
                        "lane_cell": int(lane),
                        "policy": mode,
                        "accepted": int(path is not None),
                        "reference_feasible": int(oracle is not None),
                        "validated": 0,
                        "contradicted": 0,
                        "unresolved": 0,
                        "observable_landings": 0,
                        "strict_confirmed": 0,
                        "strict_contradicted": 0,
                        "strict_unresolved": 0,
                    }
                    if path is not None:
                        see = observed[path]
                        support = ref_safe[path]
                        row["observable_landings"] = int(see.sum())
                        row["strict_confirmed"] = int(strict_safe[path].all())
                        row["strict_contradicted"] = int(
                            (strict_observed[path] & ~strict_safe[path]).any()
                        )
                        row["strict_unresolved"] = int(
                            not (row["strict_confirmed"] or row["strict_contradicted"])
                        )
                        row["contradicted"] = int((see & ~support).any())
                        row["validated"] = int(support.all())
                        row["unresolved"] = int(not (row["validated"] or row["contradicted"]))
                    routes.append(row)
    return quality, routes


def save(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", type=Path)
    ap.add_argument("calibration", type=Path)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--scenes", type=int, default=194)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    fn = partial(scene, data=a.data, calibration=a.calibration)
    with ProcessPoolExecutor(max_workers=a.jobs) as pool:
        outputs = list(pool.map(fn, range(a.scenes)))
    quality = [o[0] for o in outputs]
    routes = [r for o in outputs for r in o[1]]
    save(a.out / "scene_metrics.csv", quality)
    save(a.out / "routes.csv", routes)
    summary = []
    for coverage in [5, 7, 9]:
        for threshold in [0.06, 0.10, 0.15]:
            for policy in ["local", "graph", "graph_10cm", "graph_20cm"]:
                rows = [
                    r
                    for r in routes
                    if r["cells_required"] == coverage
                    and r["roughness_m"] == threshold
                    and r["policy"] == policy
                ]
                assert all(
                    r["accepted"] == r["validated"] + r["contradicted"] + r["unresolved"]
                    for r in rows
                )
                d = {
                    "cells_required": coverage,
                    "roughness_m": threshold,
                    "policy": policy,
                    "queries": len(rows),
                }
                for k in [
                    "accepted",
                    "reference_feasible",
                    "validated",
                    "contradicted",
                    "unresolved",
                    "strict_confirmed",
                    "strict_contradicted",
                    "strict_unresolved",
                ]:
                    d[k] = sum(r[k] for r in rows)
                d["rejected_reference_feasible"] = sum(
                    r["reference_feasible"] and not r["accepted"] for r in rows
                )
                summary.append(d)
    save(a.out / "summary.csv", summary)


if __name__ == "__main__":
    main()
