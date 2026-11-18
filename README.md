# When a foothold margin runs out of room

How much usable terrain does a footstep planner give up for a larger edge margin? This experiment lets a planner see an imperfect map and gives an independent evaluator the true patch boundaries. It counts routes that cross an edge and feasible routes that the planner turns down.

**Maintainer** · Vedant Thaker  
**Research materials** · [Manuscript (PDF)](manuscript.pdf) · [Editable manuscript](manuscript.md) · [Planning results](results.csv)

![Trade-off between accepted routes and geometrically valid routes across foothold planning conditions](figure.png)

## The planning experiment

A route crosses six rows, each with two patches and three candidate foot positions per patch. Every step must satisfy the lateral reach limit. For a 23 mm foot half-width, available clearance is the distance from the foot center to the nearer perceived edge, less 23 mm. The ordinary planner minimizes lateral travel and deviation from the travel line. A second planner first maximizes the smallest clearance anywhere on the route.

The map generator allows a patch-center shift of up to 8 mm and an additional inward loss at either edge of up to 6 mm. A 14 mm margin therefore protects the full footprint within this error envelope. An oracle solves the same finite graph using the true boundaries. This gives a denominator for feasible routes rejected by the planner.

## A narrow patch changes the trade-off

In the 1,400-layout bottleneck test with independent patch shifts, 1,335 layouts had a feasible route. Both 8 mm strategies accepted the same 1,026 layouts. Changing the route objective returned 156 more valid routes on balance.

| Route objective | Margin | Accepted | Valid | Invalid | Feasible layouts rejected |
|---|---:|---:|---:|---:|---:|
| Travel | 0 mm | 1,400 | 247 | 1,153 | 0 |
| Travel | 8 mm | 1,026 | 754 | 272 | 310 |
| Widest route | 8 mm | 1,026 | 910 | 116 | 310 |
| Travel | 14 mm | 289 | 289 | 0 | 1,046 |

Making the map errors 1.75 times larger left the perceived terrain unchanged. Of the same 289 routes accepted by the 14 mm travel rule, 130 then crossed a true edge. These are footprint checks on a finite lateral graph. Other foot placements and full-body balance constraints can change which terrain is usable.

## A source foot-plant label and a displacement budget

The companion test runs the released NVIDIA SOMA Retargeter v0.2.0 foot-plant detector on 18 synthetic source trajectories using the CPU. The detector accepted 12. At 60 mm/s, three different durations received the same confidence of 0.69 while lateral excursion grew from 15 to 30 to 60 mm. A contact label alone leaves that displacement unspecified. Applying an excursion to the route margin would require measuring the corrected robot foot in the terrain coordinate frame. [Fixture results](soma_results.csv) · [Archived upstream license](soma_modules/LICENSE) · [Upstream detector](https://github.com/NVIDIA/soma-retargeter/blob/1733b820f3cdf6f74bbc81a10bda3201b38c7bcf/soma_retargeter/pipelines/plant_subsegment_detector.py)

## Reproduce

From the repository root with Python 3.11, install the [main requirements](requirements.txt), run the simulator and verify the saved summaries.

```shell
python -m pip install -r requirements.txt
python run.py
python verify.py
```

[run.py](run.py) regenerates 120 planning conditions. [verify.py](verify.py) reads the CSVs independently with the standard library. It checks the complete grid, route counts, the 14 mm bound and the 18 SOMA fixtures. You can run it against the archived files before installing dependencies.

To repeat the source contact detector, install the [SOMA requirements](requirements-soma.txt). The CPU Warp kernel creates a local cache on its first execution.

```shell
python -m pip install -r requirements-soma.txt
python soma_check.py
python verify.py
```

To redraw the figure from the planning results, install the [plotting requirements](requirements-plot.txt) and run [make_figure.py](make_figure.py).

```shell
python -m pip install -r requirements-plot.txt
python make_figure.py
```

Run `python run.py --timings` to refresh [the optional timing sample](timings.csv). It measures a single corrected-patch map update and replanning call for 160 layouts. Machine-dependent solve times exclude perception, communication and physical execution.
