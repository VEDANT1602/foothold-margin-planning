# From stereo terrain heights to fixed-heading foot-placement decisions

The replay uses all 194 labeled KITTI Stereo 2012 training pairs. The camera system was mounted on a car. These records do not contain robot foot contacts. Script and compact numerical outputs are supplied, without images, pixel labels, laser scans, terrain grids or upstream software.

### Inputs

Download the archives directly from the [KITTI benchmark](https://www.cvlibs.net/datasets/kitti/eval_stereo_flow.php?benchmark=stereo). The exact AWS URLs and hashes are below. Retain the files as ZIP archives.

| Archive | SHA-256 |
|---|---|
| [Stereo data](https://s3.eu-central-1.amazonaws.com/avg-kitti/data_stereo_flow.zip) | 3414457882744991709c0ee97360f04bf437f1814196dfc77d7783605113eb13 |
| [Calibration](https://s3.eu-central-1.amazonaws.com/avg-kitti/data_stereo_flow_calib.zip) | 89c7535c7f53ad5ef267b94e3680f0cdd5f9b09e751befe10d5b72ed6b714981 |

Use Python 3.12 and `requirements.txt`. From the supplemental directory, execute the following.

```sh
python -m pip install -r requirements.txt
sha256sum data_stereo_flow.zip data_stereo_flow_calib.zip
OPENBLAS_NUM_THREADS=1 python terrain_routes.py data_stereo_flow.zip data_stereo_flow_calib.zip --jobs 3
python verify.py
```

### Files and units

- `scene_metrics.csv` summarizes common, observed 10 cm grid cells for each scene. Height errors compare two distinct measurements in the same stereo-estimated coordinate frame. One fit, scene 000030, failed the frame rule. The zero common-cell count records that exclusion, with empty error fields.
- `routes.csv` contains 34,740 decision records, one for each scene/lane/policy/coverage/roughness combination on the 193 valid frames. Lane offset is in cells of 10 cm. The data include no individual pixel, terrain-height measurement, footstep coordinate, or image. The fields `validated` and `strict_confirmed` mean laser-map agreement under the stated sampling rule. They say nothing about physical walking. The strict fields always demand nine cells in the laser footprint for each landing to contribute evidence. Unknown routes have no observed violation and at least one unassessed landing.
- `summary.csv` aggregates by policy and design condition. `reference_feasible` requires a path on the laser map under the matched coverage rule. `rejected_reference_feasible` is its intersection with stereo rejection.
- `verify.py` checks every partition and runs an independently written A* solver on randomized masks to test graph-optimal costs and infeasibility decisions. Tie-breaking may select different optimal paths.
- `references.md` describes experimental scope, prior evidence and the earlier simulation's denominator.

### Rights and attribution

KITTI is the work of Andreas Geiger, Philip Lenz and Raquel Urtasun (CVPR 2012). Its [copyright notice](https://www.cvlibs.net/datasets/kitti/index.php) applies [CC BY-NC-SA 3.0 Unported](https://creativecommons.org/licenses/by-nc-sa/3.0/) to the data and benchmarks. All three released CSVs are numerical results created by converting the published stereo pairs and laser-derived disparity into cell-height and route-replay summaries. These CSVs are shared under CC BY-NC-SA 3.0, with this attribution and description of modifications. The repository's MIT software license applies to original code. It does not relicense KITTI material.

To regenerate the manuscript figure, install Matplotlib 3.10.8 and run `python plot.py`.
