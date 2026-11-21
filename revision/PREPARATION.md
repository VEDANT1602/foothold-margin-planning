# Preparation record

Route coverage under bounded and probabilistic foothold-edge errors

Vedant Thaker · 21 November 2026

## Original work

Vedant Thaker is the sole author. He designed the original foothold planning study, wrote its manuscript, developed its original software, and requested the comparisons and checks reported in this revision.

The author reports that the research project began on 2 August 2026. The previous versions and the new revision represent different stages of the work.

## Revision activities

OpenAI Codex assisted with the bounded and probabilistic margin calculations, paired planning replays, stress tests for common displacement, and translation of published camera error measurements into terrain scenarios, as well as literature checks and preparation of the revised text. The author set the research question and requested the revision.

## Computational checks

The baseline planning rerun reproduced the 120-row results.csv byte for byte. Exhaustive candidate enumeration checked the dynamic program on a subset. A paired reanalysis verified fixed-cutoff acceptance equality and the 162 favorable and six unfavorable reversals. The range-dependent experiment regenerated 24 policy/terrain/bias cells. Counts reconcile as valid plus invalid equals accepted throughout. All calculations used Python 3.12.14 and NumPy 2.3.5.

## Data and version records

The baseline repository contains the original planning code and 120-row results.csv. In that checkout, python run.py regenerates the planning CSV. The accompanying supplement provides sensitivity.py, sensor_planner.py, their generated CSVs, planning-only Linux environment locks, commands and the hash of the imported benchmark module.

[Original pinned software](https://github.com/VEDANT1602/foothold-margin-planning/tree/ea643183cd45389eefb7fef70d8833efe30a5891) · [Revision code and data](https://github.com/VEDANT1602/foothold-margin-planning/tree/main/revision/supplement)

The reported checks are computational. No independent personal rerun or line-by-line review of these revisions by the author is asserted here.
