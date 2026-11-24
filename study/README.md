# Survey corroboration of ANYmal C floor patches

The study compares 30 lidar scans from the first ANYmal C robot at the DARPA Subterranean Challenge finals with the organizer's separate, downsampled course survey. The test uses either survey-registered scan poses or the motion estimated onboard during the run. This supplement contains code, a scan manifest and aggregate results. The externally hosted sensor records, survey and pose trajectories are required to rerun the reconstruction.

## Inputs

Obtain the following files from the [ETH data record](https://doi.org/10.3929/ethz-b-000552248) under **Access the files → CERBERUS_Darpa_Subt_Final_Event → anymal_1**. The dataset maintainers [describe the run-time CompSLAM trajectory, post-processed products and survey-based registration](https://github.com/leggedrobotics/cerberus_darpa_subt_datasets#final-event).

| File under anymal_1 | Identification |
| --- | --- |
| 2021-09-23-16-31-51_anymal-cerberus_mission_raw_sensors.bag | 24,591,132,760 bytes. Each consumed byte range has its own SHA-256 in quadruped_input_manifest.csv. |
| trajectories/gt_ros1.bag | SHA-256 0fb919c8addede3828da84316e6170b309ac5707e03bd3ef5da533188d77a854 |
| trajectories/1_compslam/compslam_tum.csv | SHA-256 f78c45d70144d8927ba7d8ae4d85bb395be4311872871ec8435bcc912b9c775b |

Download **data/systems_final.pcd** from the [pinned DARPA survey release](https://github.com/subtchallenge/systems_finals_ground_truth/tree/8276a16155eddf966e4458e40054bc53a31c8ac5). Its SHA-256 is 7c1502d83767de3dd112d23c294739a6c481bfbe6abb0f4d3ba563dac35ed0f7. The parser checks the input hashes.

## Reproduce the results

With Python 3.12, install the dependencies and set the two input paths below. The raw bag uses its original filename, and the two trajectory files retain their downloaded directory structure. From this directory run:

```sh
python -m pip install -r requirements.txt
robot_data=/path/to/anymal_1
course_survey=/path/to/systems_final.pcd
for anchor in 0 10; do
  OPENBLAS_NUM_THREADS=1 python quadruped_check.py \
    --bag "$robot_data/2021-09-23-16-31-51_anymal-cerberus_mission_raw_sensors.bag" \
    --poses "$robot_data/trajectories/gt_ros1.bag" \
    --online-poses "$robot_data/trajectories/1_compslam/compslam_tum.csv" \
    --survey "$course_survey" --anchor-seconds "$anchor" --out rerun
done
python verify.py rerun
```

For the released summaries only, run `python verify.py`. The full-bag and `--chunks` modes read the same byte ranges. For the latter, save each range as `chunk<bag_byte_offset>.bin`; the manifest gives its length and SHA-256. The three largest source files remain with the providers.

## Selection and interpretation

Thirty of the 32 evenly spaced targets spanning the middle 90% of the reference trajectory yielded sensor segments; the two last target segments were unavailable. Each selected segment contributed one complete rotation. Every scan header matches a reference and online trajectory timestamp. The reconstruction uses strongest-return VLP-16 packets, nominal beam angles and a single pose per rotation. The registered branch uses the reference pose supplied at each scan time. The online branch uses relative motion from the contemporaneous CompSLAM estimates, anchored by the first reference pose. A calibration sensitivity averages relative attitudes and translations over the first 10 seconds (101 earlier pose pairs). With one opening pose, the earliest evaluated scan occurs 71.10 seconds after the anchor. Both CompSLAM tests use the original set of accepted scan identifiers; the grid and which tiles qualify are recomputed for each placement.

The grid has 0.10-m cells, 340 disjoint candidate tiles per scan and a target radius of 2.5–4.0 m. The floor band extends from 1.4 to 0.2 m below the sensor. A tile meets the height-range rule if its observed maxima and minima are separated by at most 0.10 m. The implementation adds 1e-10 m solely to include floating-point representations of exact decimal boundary values. On scan 7417, tile index 681, a seven-cell survey span is represented as 0.10000000000000009 m: the inclusive rule supports it. A literal binary cutoff assigns it to the other category. This explains the five-cell registered count difference of one from the previous public version (104/13/73 here versus 103/14/73).

- `quadruped_input_manifest.csv` identifies original scan sequences, raw byte ranges, timestamps and return counts.
- `quadruped_footprints.csv`, `online_footprints.csv` and `online_10s_footprints.csv` contain a row for each scan and coverage condition for the three placements in manuscript Table 2.
- The corresponding `*_frames.csv` files report the full-window quantities. The online files additionally record elapsed time since the first pose, and differences in position and orientation from the provider's registered trajectory. They contain no pose coordinates.
- Cells absent from either map remain unobserved. The patch counts and scan-level height discrepancies quantify partial geometric agreement. They do not constitute contact measurements or independent trial-level replicates.

[Input terms](../LICENSING.md) · [Source locations](references.md)

The verification script also reports coverage as (supported + contradicted) / selected and the conditional contradiction fraction as contradicted / (supported + contradicted). Its leave-one-scan range uses all selected patches from the other 29 scans as the denominator each time. Overlapping ground coverage precludes interpreting that range as a population confidence interval.
