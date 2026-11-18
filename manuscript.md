# When a foothold margin runs out of room

**Vedant Thaker**  
Working paper · 18 November 2026

## Abstract

How much usable terrain does a footstep planner lose by adding an edge margin? The planner chooses among two patches at each of six steps. A second calculation checks the true boundaries. Among 1,400 held-out layouts with two narrow rows and independent patch shifts, a 14 mm margin admitted 289 routes. All 289 fit. Another 1,046 layouts with a feasible route were rejected. At 8 mm, minimizing lateral travel yielded 754 valid routes and 272 invalid ones. Prioritizing the route with the largest minimum clearance at that same margin yielded 910 valid routes and 116 invalid ones. Increasing map errors by a factor of 1.75 broke the 14 mm guarantee. A separate test of NVIDIA's SOMA foot-plant detector accepted 12 of 18 authored source segments. At a fixed speed, equal confidence covered different total lateral excursions. Extending a map-based guarantee to retargeted motion therefore requires a displacement bound in the terrain frame.

## From a safe-looking patch to a usable route

A contact planner needs a place for the entire foot. An estimated patch with a generous outline can contain a planned footprint whose outer edge would actually hang over the stone. Shrinking the outline gives some protection. At a bottleneck, the same operation can remove the last reachable placement. Counting only the failures among accepted routes misses that cost.

Deits and Tedrake formulate footstep selection over convex terrain regions [1]. Tonneau and colleagues' SL1M addresses the combinatorial choice of surfaces under reachability and quasi-static constraints [2]. Grandia and colleagues extract local foothold constraints from perception for a nonlinear model-predictive controller [3]. Each addresses a larger planning problem than the lateral cross-section studied here. The question here arises before a full-body controller runs. If the perceived boundary is wrong by a known amount, how much does a planning rule gain by refusing to step, and how much can it gain by choosing a different route?

The experiment makes the true boundaries available to the evaluator. This matters because a rejected map can be either impossible or simply too conservative for the planner's cutoff. Likewise, an invalid accepted plan can occur on a map with many better choices. An exhaustive check on a subset of layouts tests the reference calculation.

## A finite route with a hidden boundary

Each layout has six ordered rows. A row offers two flat patches. Their lateral centers equal a shared row offset drawn uniformly from -26 to 26 mm, plus a lane offset of -36 or +36 mm and independent jitter in [-9,9] mm. Each perceived patch half-width is uniform from 39 to 60 mm on wide terrain. On bottleneck terrain, rows three and five instead draw half-widths from 25 to 42 mm. Each patch offers its midpoint and two positions displaced by 65% of the half-width remaining after subtracting the foot half-width. A route starts at lateral coordinate zero and may move at most 56 mm laterally between successive placements. Forward progress is prescribed by row order.

For a candidate center x and perceived patch [l,r], the apparent clearance is the smaller of x-l and r-x, less a 23 mm foot half-width. Given a margin m, the ordinary planner considers only placements with clearance at least m. It minimizes total lateral travel plus one quarter of the sum of the absolute lateral coordinates. The second term favors positions near the nominal travel line. The widest-route comparator first maximizes the smallest clearance along the route and breaks ties using the same travel cost. Both planners examine the same six candidates in each row. A cutoff on the widest route preserves exactly the same set of accepted maps as a minimum-clearance constraint on every step.

The evaluator shifts each perceived patch center by a signed amount drawn uniformly from -8 to 8 mm. It moves each edge inward independently by a further 0 to 6 mm. The shift is either shared across the whole map or drawn independently for every patch. All candidate centers stay in the commanded world frame. Either boundary can move inward by at most 14 mm under this model. Therefore every accepted placement at m = 14 lies inside the true patch after allowing for the footprint. The six-step guarantee follows because all six placements satisfy the same deterministic bound. It requires no independence between edges. The 1.75-fold stress condition multiplies both shift and edge losses, allowing up to 24.5 mm of inward displacement.

The routine uses dynamic programming over consecutive rows. A separate pass searches the same candidate graph using true geometry. This oracle defines feasible rejection. A real robot could place its foot at other points, so the term refers specifically to the finite graph. Exhaustive enumeration agrees with the oracle's minimum cost on two layouts per split, error scale and correlation condition, including infeasibility where applicable.

## How many routes survive the cutoff?

The design has 600 calibration layouts, 1,400 fresh wide layouts and 1,400 fresh bottleneck layouts. Seeds are 1708, 8508 and 9508. Different policies and error scales share their underlying layouts. The comparison unit is a layout. Contacts on a route do not constitute six independent trials.

Table 1 reports the bottleneck split with independent shifts at the original error scale. Of the 1,400 layouts, 1,335 contained a valid route according to the oracle. A valid accepted route finishes all six rows. A false-feasible route fails at least one footprint test. A rejected feasible layout has a valid oracle route and receives no plan.

| Route objective | Margin, mm | Accepted | Valid | False feasible | Rejected feasible |
|---|---|---|---|---|---|
| Travel | 0 | 1400 | 247 | 1153 | 0 |
| Travel | 8 | 1026 | 754 | 272 | 310 |
| Widest | 8 | 1026 | 910 | 116 | 310 |
| Travel | 12 | 517 | 514 | 3 | 818 |
| Widest | 12 | 517 | 516 | 1 | 818 |
| Travel | 14 | 289 | 289 | 0 | 1046 |
| Widest | 0 | 1400 | 1022 | 378 | 0 |

![Figure 1](figure.png)

Figure 1. Margin, route coverage and geometric validity on 1,400 bottleneck layouts with independent patch shifts. The travel-minimizing planner uses the original error envelope. The orange series counts layouts with a feasible route on which the planner abstains.

The 8 mm rows isolate a route-choice effect. The set of maps that pass the cutoff is identical. Maximizing the narrowest clearance changes the selected placements and yields 156 additional valid completed routes on balance. The 14 mm row answers a different question. It delivers a geometric certificate for 289 plans. It leaves 78.4% of the oracle-feasible layouts unserved (1,046 of 1,335). A report giving only the success fraction of its accepted routes would show 100%.

Wide terrain changes the trade-off. With independent shifts, a 12 mm margin and the travel objective produced four invalid routes among 600 accepted calibration layouts. The same configuration on the wide test set produced 16 invalid routes among 1,400. Under the 14 mm rule all 1,400 were accepted and valid. A wide-layout evaluation alone gives little indication of the coverage loss in Table 1. Changing from independent to shared shifts on the bottleneck split leaves the number accepted at 14 mm unchanged, as it must, but changes the oracle-feasible denominator from 1,335 to 1,322.

## What breaks the certificate?

At 1.75 times the original error range, 130 of the 289 routes accepted by the 14 mm travel rule failed under independent shifts. The widened error distribution changes the actual boundary while leaving the perceived map and planner decisions fixed. All 130 layouts still had a different feasible route. An accurate error bound and a good route objective address separate failure modes. For a footprint tracker that can also move the center laterally by d mm, the same one-dimensional proof requires 14 + d mm in the original map model. A drift budget needs physical units and a common coordinate frame to enter that calculation.

To estimate one component of repair cost, the first invalid assigned patch in each of the first 160 invalid nominal bottleneck plans was rescanned before execution. The test gives the planner the truth for that patch's three candidates and resolves the route from the start. All 160 updates returned a candidate route. Other map errors remained hidden. On one AMD64 Python 3.11.9 and NumPy 1.26.0 run, the median update and solve took 0.495 ms and the 95th percentile took 0.630 ms. This small-graph timing excludes the physical scan, communication, locomotion and validation of a repaired route.

## Can a motion-retargeting contact label supply the missing margin?

NVIDIA's SOMA Retargeter identifies flat plants in a human source trajectory before it applies corrections to the robot target [4,5]. For planning, a plant label raises a separate question. How far can the center move within an interval that receives the label? The distinction matters when a downstream user has the contact label but has yet to measure the motion of the corrected robot foot.

To isolate that question, a test calls the released v0.2.0 plant-subsegment detector on 18 authored, flat, ground-level source segments. Each fixture supplies one already-detected coarse contact, identity foot orientations and synthetic heel and toe landmarks. The foot moves laterally at a constant 0, 15, 35, 60, 90 or 180 mm/s for 0.25, 0.50 or 1.00 s, sampled at 120 Hz including both endpoints. The original landmark projection runs on the CPU with NVIDIA Warp. The test also independently computes the expected decision from the released default speed and confidence gates. All 18 decisions agree.

The detector accepted all 12 segments at speeds up to 60 mm/s and rejected all six at the two higher speeds. At 60 mm/s, confidence remained 0.69 for all three durations while first-to-last lateral excursion grew from 15 to 30 to 60 mm. The same label and confidence therefore do not determine an excursion budget. For a one-second accepted source segment at 35 mm/s, transferring its uncorrected motion one-for-one from a centered start would raise the required geometric margin from 14 to 49 mm. That is a conditional calculation. The vendor's downstream correction is meant to alter the target trajectory. The test never measures a corrected robot foot or establishes the motion of any particular robot. To use the planning guarantee after retargeting, measure the corrected foot's maximum displacement relative to its commanded center in the terrain frame.

## Interpretation and replication

The finite graph makes abstention measurable and the error certificate inspectable. It also excludes foot yaw, longitudinal overhang, compliance, loss of traction, balance and moving contacts. Overlap with a different patch does not rescue a footprint outside its assigned patch. The uniform errors and tolerances are test settings. No depth camera or robot supplied those distributions. A physical follow-up would register a sequence of measured stone boundaries against ground truth, retain map-wide correlations and replay the route choices before attempting hardware trials.

Run python run.py with Python and NumPy to regenerate the 120 condition rows in results.csv. The optional command python run.py --timings also repeats the machine-dependent timing sample. The script includes the general maximum-inward-error assertion and independent exhaustive-cost checks. The central empirical conclusion is conditional on the chosen graph and error model. At a fixed acceptance rate, a route objective can recover useful geometric margin. At a fixed worst-case guarantee, the remaining question is how much terrain the robot can still use.

## Research and writing assistance

Vedant Thaker supplied the research brief and source materials. OpenAI Codex assisted with study design, implementation, execution, literature review and drafting. Clever Humanizer suggested edits to the abstract. The final wording was checked against the analysis.

## References

[1] R. Deits and R. Tedrake. Footstep planning on uneven terrain with mixed-integer convex optimization. IEEE-RAS International Conference on Humanoid Robots, 2014. https://dspace.mit.edu/entities/publication/394a432f-d7f2-4061-b8ca-86c4996110d6

[2] S. Tonneau, D. Song, P. Fernbach, N. Mansard, M. Taïx and A. Del Prete. SL1M: Sparse L1-norm minimization for contact planning on uneven terrain. IEEE International Conference on Robotics and Automation, 2020. https://doi.org/10.1109/ICRA40945.2020.9197371

[3] R. Grandia, F. Jenelten, S. Yang, F. Farshidian and M. Hutter. Perceptive locomotion through nonlinear model-predictive control. IEEE Transactions on Robotics, 2023. https://arxiv.org/abs/2208.08373

[4] J. Malaska. Adapt Human Motion for Robots with NVIDIA SOMA Retargeter. NVIDIA Technical Blog, 2026. https://developer.nvidia.com/blog/adapt-human-motion-for-robots-with-nvidia-soma-retargeter

[5] NVIDIA. SOMA Retargeter v0.2.0. Plant subsegment detector and default configuration. The companion script soma_check.py uses the archived modules and warp-lang 1.14.0 to regenerate soma_results.csv. https://github.com/NVIDIA/soma-retargeter/blob/1733b820f3cdf6f74bbc81a10bda3201b38c7bcf/soma_retargeter/pipelines/plant_subsegment_detector.py
