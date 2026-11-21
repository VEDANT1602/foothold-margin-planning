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

## Registered ANYmal lidar and DARPA course survey

Obtain `anymal_1/2021-09-23-16-31-51_anymal-cerberus_mission_raw_sensors.bag` (24,591,132,760 bytes) and `anymal_1/trajectories/gt_ros1.bag` from the **Access the files** link of the [ETH record](https://doi.org/10.3929/ethz-b-000552248). The research archive lists “In Copyright – Non-Commercial Use Permitted.” See its [rights statement](https://rightsstatements.org/page/InC-NC/1.0/) before reusing source data. The [organizer's survey](https://github.com/subtchallenge/systems_finals_ground_truth/tree/8276a16155eddf966e4458e40054bc53a31c8ac5) is `data/systems_final.pcd`. The two SHA-256 digests below identify the pose bag and the survey. For the raw sensor bag `quadruped_input_manifest.csv` gives a SHA-256, length and seek position for every consumed range. These files need no network access once obtained.

```sh
python quadruped_check.py --bag /data/2021-09-23-16-31-51_anymal-cerberus_mission_raw_sensors.bag --poses /data/gt_ros1.bag --survey /data/systems_final.pcd --out rerun
```

- Pose-bag SHA-256 `0fb919c8addede3828da84316e6170b309ac5707e03bd3ef5da533188d77a854`; survey SHA-256 `7c1502d83767de3dd112d23c294739a6c481bfbe6abb0f4d3ba563dac35ed0f7`.
- Thirty target scan segments were available out of 32 equally spaced targets over the middle 90% of the published pose timestamps. The last two segments were unavailable to this analysis. For each target we found the nearest indexed chunk with at least one `/lidar/packets` message and took its first rotation. The input manifest fixes the exact selected scans. Points come from the strongest-return mode, VLP-16 nominal elevation sequence and 2-mm distance scale. Horizontal azimuth is interpolated within each 12-block packet, with the last block reusing the penultimate azimuth increment. Points use ROS x-forward/y-left/z-up. Packet deskew, beam-specific factory corrections and local ICP refinements are omitted. The published scan-pose stamp equals the scan header timestamp in all 30 samples. We checked the direct transform against floor and wall returns and applied it as supplied. The source authors registered individual VLP-16 scans to the DARPA survey to derive the referenced trajectory; that shared alignment precludes independent localization evaluation.
- `quadruped_footprints.csv` gives one row per frame and observed-cell rule. A frame has 340 disjoint square tiles with centers between radii 2.5 m and 4 m, 0.1 m cells, a −1.4 to −0.2 m floor-height window and 0.1 m observed-height-range tolerance. At least one return sets a cell height. Overhangs and material friction are outside the definition. `quadruped_frames.csv` gives the shared-cell counts and median absolute height difference in the full grid. Neither individual raw sensor points nor the external survey, sensor frames or trajectory values are redistributed.
- The existing KITTI-derived outputs remain covered by the upstream CC BY-NC-SA 3.0 terms and original attribution. Study software and third-party data have distinct licenses. The paper reports aggregate counts for the legged-robot check. Inclusion or relicensing of any source data or derivative road products requires checking the relevant terms for the specific outlet.
