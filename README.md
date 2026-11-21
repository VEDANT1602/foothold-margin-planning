# Can a laser reference corroborate foot placements selected from stereo terrain maps?

Technical report by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana. Correspondence: vedant.thaker1602@gmail.com.

A stereo map can support a sequence of apparently level footprints even when a second sensor has insufficient coverage to evaluate them. A fixed-heading foot-placement graph was replayed on all 194 labeled KITTI Stereo 2012 scenes. In 193 usable terrain frames, 965 lane queries compared a local nearest-step rule with graph search. With five of nine cells required per footprint and a 10 cm height-range limit, the search proposed 468 paths. The registered laser map supported 326 under the same rule, contradicted 18 and left 124 unresolved. Adding 10 cm of map clearance reduced the counts to 199 supported, three contradicted and 69 unresolved. Requiring complete laser coverage of every footprint corroborated none of the original 468 paths and still contradicted 15. The result identifies which landing decisions a real second sensor can dispute and how much accepted coverage is lost to a clearance margin. No physical steps were executed.

- [Read the paper](manuscript.pdf)
- [Read the plain-text manuscript](manuscript.md)
- [Reproduce the analysis and inspect the source and data records](study/README.md)
- [Software license](LICENSE) and [third-party terms](LICENSING.md)
- [Preparation record](study/PREPARATION.md)
- [Previous manuscript and supplements](https://github.com/VEDANT1602/foothold-margin-planning/tree/6e6751dac579e40a6da626b90d13b8f34ccf6a48)
