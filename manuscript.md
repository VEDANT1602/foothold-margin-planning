# How much of a candidate foothold does a second terrain map observe?

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

Terrain mapping study · November 24, 2026

### Abstract

A course survey can check whether a patch looks level only where it has measured the floor. Thirty lidar scans from one ANYmal C traverse yielded 10,200 candidate scan–tile observations. After per-scan registration to the survey, 190 tiles had at least five occupied robot cells and an observed height range of at most 0.10 m. With the same five-cell coverage requirement, the survey supported 104 selections, contradicted 13 and left 73 unresolved. Requiring complete survey coverage made only 13 of those 190 selections assessable. Placing the same scans with onboard motion and a single opening survey anchor gave 194 selections, with 77 supported, 49 contradicted and 68 unresolved. Both how much the survey observes and how the scans are placed affect the apparent agreement on this traverse.

## Two ways of placing a scan on the course survey

An elevation map can report a level patch while missing its edge. Two quantities matter when another map is used to check that judgement. Coverage is the fraction of selected patches for which the survey has enough observed cells. Conditional disagreement is the fraction exceeding the height-range limit among those assessable patches. Keeping the denominators separate shows what the survey actually measured.

The CERBERUS release contains onboard VLP-16 lidar scans and trajectories from an ANYmal C at the DARPA Subterranean Challenge finals in the Louisville Mega Cavern [1–3]. The organizer released a separate course survey, downsampled to one million points [4]. The CERBERUS team registered the robot's scans to the survey to obtain reference poses. Those poses allow a comparison at corresponding locations, but they use the same map that grades the decisions. We therefore also test the trajectory estimated onboard by CompSLAM during the run.

We used 30 full lidar rotations from the first listed robot. They cover 20.0 minutes with about 41 seconds between scans. The original sample requested 32 times spanning the middle 90% of the reference trajectory. The last two sensor segments were unavailable. All reported comparisons use the same 30 scans in time order. The archive and the supplement identify each scan.

## Floor patches and missing measurements

We decoded strongest-return VLP-16 packets using nominal beam elevations, a 2-mm range increment and a within-packet azimuth interpolation [5]. We used one pose per rotation. In a gravity-level 9 × 9 m window around the sensor, we kept returns 0.20–1.40 m below it and used a 0.10-m grid oriented to the horizontal projection of the laser's x-axis. For the onboard lidar we retained ranges of 0.75–8 m. Each occupied grid cell received the median height of its returns. The filter can exclude elevated obstacles. Swing clearance, material friction and physical support are outside this measurement.

Each scan has 340 disjoint 0.30 × 0.30 m candidate tiles centered 2.5–4.0 m from the laser. Each tile contains nine cells. For the main comparison a robot tile must have at least five occupied cells and an observed height range of at most 0.10 m. A survey tile with sufficient coverage **supports** the selection if it satisfies the same height limit, or **contradicts** it if the range exceeds the limit. A survey tile with insufficient coverage is **unresolved** regardless of the available heights. Five- and seven-cell thresholds were examined after requiring all nine robot cells yielded no qualifying tiles. The resulting counts are exploratory. Successive scans can revisit the same floor, so we report counts without treating scan–tile observations as independent.

| Robot cells required | Survey cells required | Robot selected | Survey supports | Contradicts | Unresolved |
| --- | --- | --- | --- | --- | --- |
| 3 | 3 | 584 | 427 | 85 | 72 |
| 5 | 5 | 190 | 104 | 13 | 73 |
| 5 | 9 | 190 | 12 | 1 | 177 |
| 7 | 7 | 14 | 4 | 0 | 10 |
| 9 | 9 | 0 | 0 | 0 | 0 |

Table 1. All rows use the provider's per-scan survey registration. The two rows with five required robot cells refer to the identical 190 patches. The 0.10 m height-range threshold includes equality.

Across the full windows, the registered maps share 9,262 occupied cells. The median across scans of the within-scan median absolute height difference is 39.6 mm (interquartile range 33.2–66.2 mm). In this placement, 117/190 selections (61.6%) have at least five survey cells. Of those, 13/117 (11.1%) exceed the height-range limit. Requiring all nine survey cells reduces the assessable fraction to 13/190 (6.8%). Even an observed pass based on five cells leaves up to four cells unchecked.

## Agreement under onboard localization

For a second placement of each scan, we used the relative motion in the provider's synchronized **in-operation CompSLAM** trajectory. If the online pose at time *t* is *E(t)* and the first reference pose is *G(0)*, the test pose is *G(0) E(0)⁻¹ E(t)*. Only the opening reference pose enters this alignment. It precedes every evaluated scan by at least 71 seconds. A constant rigid change of coordinates for the entire online trajectory cancels in the relative transformation. We recomputed the robot and survey grids under the resulting pose, with identical ranges, tile indices and height limits. Changes in estimated attitude can alter which robot tiles qualify, so each row has its own selected denominator.

| Pose and calibration | Robot selected | Survey supports | Contradicts | Unresolved | Shared cells | Median gap (mm) |
| --- | --- | --- | --- | --- | --- | --- |
| Survey registration per scan | 190 | 104 | 13 | 73 | 9,262 | 39.6 |
| Online motion, first pose | 194 | 77 | 49 | 68 | 6,966 | 266.5 |
| Online motion, first 10 seconds | 192 | 78 | 47 | 67 | 6,813 | 318.1 |

Table 2. All rows use five observed cells per map and the same 30 scans. The last column is the median of the 30 scan-level median absolute height differences. Shared cells are counted over the full windows, while the tile decisions use the smaller radial band.

With one initial pose, the median separation of the online-derived lidar origins from their registered counterparts is 1.65 m and the median orientation difference is 3.33°. With this placement, 126/194 selections (64.9%) have sufficient survey coverage, close to the registered placement’s 61.6%. Among those assessable tiles, 49/126 (38.9%) exceed the height-range limit, compared with 13/117 (11.1%) under per-scan registration. This compares the selections made by each placement. A difference in these fractions does not identify individual tiles that changed classification. In a sensitivity analysis prompted by the size of that difference, we fitted a constant transform to the first 10 seconds (101 paired poses). Its rotation averages differences between paired attitudes, and its translation averages the position residuals after rotation. The last calibration pose still precedes the first evaluation by over a minute. There are 47 contradictions among 192 selections (24.5%). Both calibrations therefore produce materially more measured disagreements than per-scan registration on this traverse. The data alone do not apportion that increase among drift, initial alignment, imperfect scan timing and differences in which structures the two sensors observed.

## Coverage across the traverse

Contradictions in the registered five-cell comparison occur in seven of the thirty scans. They occur in twenty scans with the one-pose onboard alignment. Leaving out any one scan gives 5.0–7.7% contradictions among all remaining selections for the registered placement and 22.9–28.0% for onboard motion. These ranges test whether a single scan drives the observed contrast. Revisits to the same terrain still limit transfer across routes.

Sparse survey coverage leaves some apparently level patches unassessed. Registration to the scoring survey also favors geometric agreement relative to using onboard motion. These results describe the observed parts of candidate patches on one traverse. The online check uses a separate localization estimate for the evaluated times, but shares the robot, lidar, opening survey alignment and course with the primary comparison. Neither placement provides a contact outcome. Transfer to another course requires a new traverse with a surveyed support surface and a pose reference independent of that surface. Claims about foot-placement safety would additionally require foot locations and observed landings.

Villarreal et al. measured approximately 3 cm of foothold-prediction uncertainty associated with trunk-state estimates and separately observed 2.5 cm of map drift after roughly 2 m of travel on their robot [6, §IV-C(c)]. Their measurements address different errors and neither sets the 0.10-m terrain height limit in this study.

## Data and code availability

The ETH CERBERUS archive [1] supplies the original sensor bag and both trajectories. The organizer supplies the separately acquired survey [4]. The study directory contains a 30-scan selection manifest with bag offsets and hashes, a parser for the selected ranges, instructions for reconstructing the grids, and the scan-level result tables. Run `python verify.py` in `study/` to recalculate the manuscript counts from those tables. Raw sensor and survey records remain at the providers under their respective terms.

Study directory: <https://github.com/VEDANT1602/foothold-margin-planning/tree/main/study>.

## Author and disclosures

Vedant Thaker is the sole author and specified the comparison between robot-selected patches and a surveyed surface. OpenAI Codex assisted with scan decoding, trajectory comparisons, calculations, source checks and drafting, including the coverage-denominator and leave-one-scan comparisons.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] M. Tranzatto, L. Bernreiter and S. M. K. Khattak. CERBERUS DARPA Subterranean Challenge – Final Event. ETH Zürich Research Collection, 2022. <https://doi.org/10.3929/ethz-b-000552248>

[2] CERBERUS dataset maintainers. Final Event, Trajectories per robot and Ground-Truth. <https://github.com/leggedrobotics/cerberus_darpa_subt_datasets#final-event>

[3] M. Tranzatto et al. CERBERUS in the DARPA Subterranean Challenge. Science Robotics 7, eabp9742 (2022). <https://doi.org/10.1126/scirobotics.abp9742>

[4] DARPA Subterranean Challenge. Systems Finals Ground Truth. Downsampled course survey, release 8276a16. <https://github.com/subtchallenge/systems_finals_ground_truth/tree/8276a16155eddf966e4458e40054bc53a31c8ac5>

[5] Velodyne Lidar. VLP-16 User Manual, revision F. Laser channel positions and azimuth interpolation. <https://data.ouster.io/downloads/velodyne/user-manual/vlp-16-user-manual-revf.pdf>

[6] O. Villarreal, V. Barasuol, M. Camurri, L. Franceschi, M. Focchi, M. Pontil, D. G. Caldwell and C. Semini. Fast and continuous foothold adaptation for dynamic locomotion through CNNs. IEEE Robotics and Automation Letters 4(2), 2140–2147 (2019). <https://doi.org/10.1109/LRA.2019.2899434> · [Authors’ PDF, page 5](https://iit-dlslab.github.io/papers/villarreal19ral.pdf#page=5)
