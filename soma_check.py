"""Conditional foot-plant test. Run with numpy and warp-lang==1.14.0 installed."""
import csv
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import warp as wp


HERE = Path(__file__).resolve().parent
wp.config.kernel_cache_dir = str(HERE / ".warp_cache")
wp.init()
wp.set_device("cpu")
sys.path.insert(0, str(HERE / "soma_modules"))
from soma_retargeter.animation.contact_phase import FootLandmarkModel, FootLandmarkRuntime
from soma_retargeter.pipelines.plant_subsegment_detector import detect_plant_subsegments


def landmarks():
    feet = []
    for side, name in enumerate(("Left", "Right")):
        feet.append(FootLandmarkRuntime(
            side, name+"Foot", name+"ToeBase", None, 2*side, 2*side+1, -1,
            np.array([-0.04, 0, 0]), np.array([0.04, 0, 0]),
            np.array([0, 0, 1]), "foot"))
    return FootLandmarkModel("fixture", feet)


def evaluate(speed_mm_s, duration_s):
    fps = 120
    n = round(fps*duration_s)+1
    t = np.arange(n)/fps
    transforms = np.zeros((n,4,7), dtype=np.float32)
    transforms[:,:,6] = 1
    transforms[:,:2,1] = (t * speed_mm_s / 1000)[:,None]
    speed = np.full((n,1), speed_mm_s / 1000)
    segment = SimpleNamespace(joint_channel=0, start_frame=0, end_frame=n)
    inputs = SimpleNamespace(speed=speed, contact_segments=[segment])
    result = detect_plant_subsegments(
        inputs, None, None, None, "fixture", ["LeftFoot"], {0:0},
        all_global_tx=transforms, landmark_model=landmarks())
    accepted = bool(result.subsegments)
    if accepted:
        assert (result.subsegments[0].start_frame, result.subsegments[0].end_frame) == (0,n)
    expected = speed_mm_s/1000 < 0.15 and 1.15*(1 - speed_mm_s/150) >= .5
    assert accepted == expected
    excursion = 1000.0*float(np.max(transforms[:,0,1]) - np.min(transforms[:,0,1]))
    assert abs(excursion-speed_mm_s*duration_s) < 1e-4
    return dict(speed_mm_s=speed_mm_s, duration_s=duration_s, frames=n, plant_accepted=int(accepted),
                confidence=round(result.subsegments[0].confidence,6) if accepted else "",
                excursion_mm=round(excursion,4), required_margin_if_transferred_mm=round(14+excursion,4))


def main():
    rows = [evaluate(v,t) for v in (0,15,35,60,90,180) for t in (.25,.5,1.)]
    with (HERE / "soma_results.csv").open("w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("Accepted",sum(r["plant_accepted"] for r in rows),"of",len(rows))


if __name__ == "__main__":
    main()
