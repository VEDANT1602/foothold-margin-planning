# Route coverage under bounded and probabilistic foothold-edge errors

Vedant Thaker · November 21, 2026

A foothold planner can protect accepted routes by rejecting terrain that a different route could traverse. This study measures that cost on a six-row lateral graph.

- [Revised manuscript (PDF)](manuscript.pdf) · [Editable manuscript](manuscript.md)
- [Revision code, results and reproduction instructions](revision/supplement/) · [Preparation record](revision/PREPARATION.md)
- [Baseline software and results at the study commit](https://github.com/VEDANT1602/foothold-margin-planning/tree/ea643183cd45389eefb7fef70d8833efe30a5891) · [Software license](LICENSE) · [Third-party terms](LICENSING.md)

## Earlier study and reproduction instructions

The following instructions and results describe the original study. The revised paper and its supplemental tests are linked above.

### Reproduce the planning baseline

Install the baseline requirements, run python run.py, then python verify.py. The root verifier checks all 120 planning conditions and the deterministic 14 mm bound. The original mixed-scope source, third-party notices and its original instructions remain in the [pinned baseline](https://github.com/VEDANT1602/foothold-margin-planning/tree/ea643183cd45389eefb7fef70d8833efe30a5891).

