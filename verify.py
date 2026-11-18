"""Independently verify archived route counts and source foot-plant fixtures."""
import csv
from itertools import product
from math import isclose
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    with (HERE / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def check_routes():
    records = read("results.csv")
    margins = ("0", "4", "8", "10", "12", "14", "widest", "widest_8", "widest_12", "widest_14")
    layouts = {"calibration": 600, "wide_test": 1400, "pinch_test": 1400}
    indexed = {(r["split"], r["correlation"], float(r["error_scale"]), r["margin_mm"]): r for r in records}
    grid = set(product(layouts, ("shared", "independent"), (1., 1.75), margins))
    require(len(records) == len(grid) and indexed.keys() == grid, "Unexpected planning condition grid")
    for key, row in indexed.items():
        split, correlation, scale, margin = key
        n = int(row["layouts"])
        oracle = int(row["oracle_feasible"])
        accepted, valid, failed, rejected, alternative = map(int, (
            row["accepted"], row["valid_accepted"], row["false_feasible"], row["rejected_feasible"],
            row["alternative_exists"],
        ))
        require(n == layouts[split] and 0 <= valid <= accepted <= n and 0 <= oracle <= n, f"Counts: {key}")
        require(accepted == valid + failed and oracle == valid + alternative + rejected, f"Accounting: {key}")
        require(0 <= alternative <= failed and 0 <= rejected <= n - accepted, f"False and rejected counts: {key}")
        if margin in ("14", "widest_14") and scale == 1:
            require(failed == 0, f"Within-envelope 14 mm violation: {key}")
        if margin.startswith("widest_"):
            ordinary = indexed[split, correlation, scale, margin.split("_")[1]]
            require(accepted == int(ordinary["accepted"]) and rejected == int(ordinary["rejected_feasible"]),
                    f"Cutoff acceptance differs between objectives: {key}")
    for margin, expected in [("0", (1400, 247, 1153, 0)), ("8", (1026, 754, 272, 310)),
                              ("widest_8", (1026, 910, 116, 310)), ("14", (289, 289, 0, 1046))]:
        row = indexed["pinch_test", "independent", 1., margin]
        counts = tuple(int(row[k]) for k in ("accepted", "valid_accepted", "false_feasible", "rejected_feasible"))
        require(counts == expected and int(row["oracle_feasible"]) == 1335, f"Bottleneck table: {margin}")
    stressed = indexed["pinch_test", "independent", 1.75, "14"]
    require(int(stressed["accepted"]) == 289 and int(stressed["false_feasible"]) == 130,
            "Out-of-envelope stress result differs")


def check_plants():
    records = read("soma_results.csv")
    indexed = {(int(r["speed_mm_s"]), float(r["duration_s"])): r for r in records}
    grid = set(product((0, 15, 35, 60, 90, 180), (.25, .5, 1.)))
    require(len(records) == len(grid) and indexed.keys() == grid, "Unexpected plant fixture grid")
    accepted = 0
    for (speed, duration), row in indexed.items():
        labeled = int(row["plant_accepted"])
        accepted += labeled
        excursion = speed * duration
        require(labeled == int(speed <= 60), f"Archived decision differs at {speed} mm/s for {duration} s")
        require(int(row["frames"]) == round(120*duration) + 1 and isclose(float(row["excursion_mm"]), excursion),
                f"Sampling or excursion differs at {speed} mm/s for {duration} s")
        require(isclose(float(row["required_margin_if_transferred_mm"]), 14.+excursion),
                f"Conditional displacement budget differs at {speed} mm/s for {duration} s")
        if speed == 60:
            require(isclose(float(row["confidence"]), .69), "60 mm/s confidence differs")
    require(accepted == 12, f"Expected 12 accepted source segments, obtained {accepted}")


if __name__ == "__main__":
    check_routes()
    check_plants()
    print("Verified 120 planning conditions, the 14 mm certificate, the stressed case and 18 SOMA fixtures.")
