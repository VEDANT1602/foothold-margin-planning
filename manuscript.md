# Can a laser reference corroborate foot placements selected from stereo terrain maps?

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

21 November 2026

### Abstract

A stereo map can support a sequence of apparently level footprints even when a second sensor has insufficient coverage to evaluate them. A fixed-heading foot-placement graph was replayed on all 194 labeled KITTI Stereo 2012 scenes. In 193 usable terrain frames, 965 lane queries compared a local nearest-step rule with graph search. With five of nine cells required per footprint and a 10 cm height-range limit, the search proposed 468 paths. The registered laser map supported 326 under the same rule, contradicted 18 and left 124 unresolved. Adding 10 cm of map clearance reduced the counts to 199 supported, three contradicted and 69 unresolved. Requiring complete laser coverage of every footprint corroborated none of the original 468 paths and still contradicted 15. The result identifies which landing decisions a real second sensor can dispute and how much accepted coverage is lost to a clearance margin. No physical steps were executed.

## A route can outlive its sensor evidence

A legged planner must decide whether a surface has enough support for a foot. Nearest-foothold adaptation and longer-horizon search can both return a path on a map with gaps. A second sensor offers a direct test of the chosen landings, provided it observes them. Counting every uncontradicted path as successful hides this distinction. This study preserves three outcomes for each selected route: agreement on all landings, at least one measured contradiction, or insufficient reference coverage.

KITTI Stereo 2012 pairs roadway stereo images with a laser-derived disparity reference [1]. These recordings allow a specific question: when two sensing modalities inspect the same footprints, how does a margin change agreement, contradiction and the number of rejected lanes? The benchmark supplies observations for the map-level decision. A car collected the images and a foot-placement lattice was overlaid offline. There are no force, slip, step-tracking or robot-stability measurements.

## Two terrain maps for each scene

The input is the complete public training split of 194 static scenes [1]. OpenCV StereoSGBM, in three-way mode, estimates disparity from the rectified grayscale pair [2]. Its fixed settings use 96 disparity levels, a 5-pixel matching block and a uniqueness ratio of 10. The reference comes from KITTI’s non-occluded disparity product constructed from registered laser sweeps. It contains gaps after projection and manual exclusion of ambiguous regions. Stereo and laser share the calibration and the coordinate frame; these residuals therefore omit common frame error.

Each disparity source is back-projected with the supplied rectified camera matrices. A robust plane fit to central stereo points in a nominal road-height band defines the origin and up direction. No laser value enters the plane estimate or route selection. Points in front of the camera are rasterized at 0.10 m resolution over a 9 × 9 m region beginning 6 m ahead. A cell receives the median height of its points if at least two contribute. One scene (000030) failed the frame test, leaving 193 scenes and 965 of the 970 possible lane queries. The two maps had 897,930 common observed cells. Across scenes the median of the scene-wise median absolute height differences was 14.0 mm, with interquartile range 12.1–16.2 mm. Such an error summary gives no guarantee that the chosen steps agree.

A footprint spans 3 × 3 cells. The observed heights must lie within 0.40 m above or below the estimated ground plane, and their range must be at most 0.06, 0.10 or 0.15 m. We vary the minimum observed count between five, seven and nine cells. Missing heights are never filled. With a partial footprint, a passing decision refers only to the available cells. The five- and seven-cell rules were examined after the complete-cell rule produced zero stereo routes. This is an exploratory benchmark.

## Local adaptation and look-ahead on a common graph

Each scene supplies five equally spaced lane centerlines. A query requests 15 alternating foot placements spaced 0.40 m forward, spanning 5.60 m. The nominal left/right offsets are −0.20 m and +0.20 m. On intermediate rows, 17 candidate lane offsets span ±0.80 m at 0.10 m spacing. Consecutive lane offsets can change by at most 0.20 m, in addition to the nominal alternation. The first and last offsets are fixed at zero, giving up to 223 nodes per query. The model fixes heading and does not represent body or swing-foot collisions.

The local rule chooses the reachable admissible site closest to the nominal foot position. Villarreal et al. used this principle after applying their robot-specific reach, terrain and collision checks [3]. The global comparator searches a finite set of alternating footstep actions, following the planning structure of Chestnutt et al. [4]. Here all edges advance one row, so dynamic programming exactly minimizes the sum of absolute lane offset and absolute change in offset, in grid cells. The code and action set are specific to this replay. The published ASIMO system used A* with its own state-dependent actions and controller.

For each rule, the stereo map alone supplies eligible sites. The global planner can additionally exclude centers lying within 0.10 or 0.20 m of a failed or insufficiently observed center, using Euclidean grid-center distance. The laser reference then evaluates the selected route at the same 15 locations. Agreement requires all to qualify. Contradiction requires one or more observable landings violating the height rules. Other accepted paths remain unresolved. A separate laser-only graph search records whether any qualifying route exists in that lane. An unresolved selected path can coexist with another fully assessable path.

## Clearance trades confirmed coverage for fewer contradictions

At the five-cell, 0.10 m height-range rule, the local selector found 429 paths; global search found 468. Of the 626 lanes admitting a laser-reference route, 250 were rejected by the local selector and 219 by the global search. Adding 0.10 m of clearance to that search rejected 386 of the 626. It removed 15 observed contradictions from the aggregate count, while the number of reference-supported paths fell by 127. The lane, footprint and sensor settings must accompany either comparison.

The measured contradictions are a lower bound on contradictions among all proposed paths. With 124 unresolved outcomes, the no-margin graph’s potential count ranges from 18 to 142 of 468 if the missing evidence could resolve either way. On the same interpretation, 0.10 m clearance gives 3 to 72 of 271. These are identification bounds under the selected footprint rule. No independence assumption about successive landings or overlapping lanes is needed.


| Stereo policy | Proposed | Agree | Disagree | Unknown | Feasible lanes rejected |
| --- | --- | --- | --- | --- | --- |
| Local nearest | 429 | 306 | 14 | 109 | 250 |
| Graph | 468 | 326 | 18 | 124 | 219 |
| Graph + 0.10 m | 271 | 199 | 3 | 69 | 386 |
| Graph + 0.20 m | 130 | 98 | 2 | 30 | 507 |
Table 1. Five occupied cells required per footprint in each map, 0.10 m height-range limit. Each row covers the same 965 lane queries. The final column counts stereo rejections among 626 laser-reference-feasible lanes.

## What changes when the reference must see all nine cells?

Keeping the original 468 paths fixed while demanding a complete nine-cell laser footprint at every landing leaves zero fully corroborated routes. Fifteen contain at least one completely observed violation. The remaining 453 are unresolved. The analogous test on the 271 paths with a 0.10 m margin finds one contradicted and 270 unresolved. Five sampled cells can corroborate an observed height range, while a hazard on one of the other four cells could go undetected.

Changing both maps to seven cells cut proposed paths from 468 to 188. Changing both to nine eliminated them despite 23 laser-feasible lane queries. Varying the height-range limit while retaining the five-cell rule had a smaller effect on proposed routes (Table 2). The result depends on the chosen 0.10 m grid, coverage requirement and route length. Counting the five lanes per scene as independent replicates would understate their shared scene and calibration effects.


| Cells required | Height range (m) | Proposed | Agree | Disagree | Unknown | Laser feasible |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.06 | 445 | 307 | 18 | 120 | 612 |
| 5 | 0.10 | 468 | 326 | 18 | 124 | 626 |
| 5 | 0.15 | 483 | 341 | 11 | 131 | 642 |
| 7 | 0.10 | 188 | 39 | 10 | 139 | 317 |
| 9 | 0.10 | 0 | 0 | 0 | 0 | 23 |
Table 2. Unmargined graph search on the same 965 lanes. Each row applies the indicated cell and height rules to both sensors.

![Figure 1. The same 468 selected stereo routes evaluated with two laser coverage rules. The narrower red segment contains 18 contradicted routes at five cells and 15 at nine. Complete reference coverage confirms no entire route.](study/laser-coverage.png)

## What the margin means in a robot

Villarreal et al. observed about 2.5 cm of short-term map drift after roughly 2 m of robot motion and separately reported 3 cm uncertainty around nominal foothold prediction [3]. Neither quantity sets a KITTI map margin. The grid erosion here removes candidates close to an observed failure or coverage boundary. It does not bound drift, and a single-frame comparison cannot reproduce drift accumulation.

The two maps agree on some partial footprints and explicitly disagree on others. Their missing observations sharply limit what can be concluded about a whole path, even when typical height residuals are small. A field decision requires tracked robot foot poses, an independently surveyed or contact-labeled support surface, and repeated traversals that include rejected terrain. Only those data could connect the map disagreement measured here to a probability of stepping failure.

## Data and code availability

The KITTI Stereo 2012 data and calibration are available from https://www.cvlibs.net/datasets/kitti/eval_stereo_flow.php?benchmark=stereo . The accompanying supplement gives exact input hashes, software versions, route classifications, summary tables and reproduction commands. The KITTI-derived tables retain CC BY-NC-SA 3.0 attribution and terms. Source imagery and laser measurements remain with the provider.

[Study files, software and source records](https://github.com/VEDANT1602/foothold-margin-planning/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author and set the research question. OpenAI Codex assisted with processing the stereo and laser reference measurements, implementing the planning comparisons and drafting the analysis.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] A. Geiger, P. Lenz and R. Urtasun. Are we ready for autonomous driving? The KITTI Vision Benchmark Suite. IEEE Conference on Computer Vision and Pattern Recognition, 3354–3361, 2012. <https://doi.org/10.1109/CVPR.2012.6248074>

[2] OpenCV. StereoSGBM class reference, version 4.12.0. Disparity matching API and implementation settings. <https://docs.opencv.org/4.12.0/d2/d85/classcv_1_1StereoSGBM.html>

[3] O. Villarreal, V. Barasuol, M. Camurri, L. Franceschi, M. Focchi, M. Pontil, D. G. Caldwell and C. Semini. Fast and continuous foothold adaptation for dynamic locomotion through CNNs. IEEE Robotics and Automation Letters 4(2), 2140–2147, 2019. <https://doi.org/10.1109/LRA.2019.2899434>

[4] J. Chestnutt, M. Lau, G. Cheung, J. Kuffner, J. Hodgins and T. Kanade. Footstep planning for the Honda ASIMO humanoid. IEEE International Conference on Robotics and Automation, 629–634, 2005. <https://publications.ri.cmu.edu/footstep-planning-for-the-honda-asimo-humanoid>
