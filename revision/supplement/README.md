# Planning under uncertain lateral support boundaries

The [public baseline](https://github.com/VEDANT1602/foothold-margin-planning/tree/ea643183cd45389eefb7fef70d8833efe30a5891) supplies a dependency-free graph description plus a NumPy implementation of terrain generation, shortest feasible path search and widest-path search. Download the pinned checkout. Both scripts verify the SHA-256 of its planning module before import. The bundle contains numerical outputs and newly written planning analyses. The original paper's figure can be found in that pinned checkout.

For the revision, activate a clean Linux x86_64 CPython 3.12.14 environment and run:

```sh
python -m pip install --require-hashes -r revision-cp312-linux-x86_64.lock
python sensitivity.py /path/to/foothold-margin-planning
python sensor_planner.py /path/to/foothold-margin-planning
```

The first command installs NumPy 2.3.5. The second analysis outputs stress.csv and paired.csv for the bounded uniform-error benchmark. The new sensor_planner.py writes chance_results.csv for 24 policy/terrain/drift settings. The source of the sensor precision model is C. Nguyen et al., DOI 10.1109/3DIMPVT.2012.84, Eqs. 1–2; the independent Gaussian sampler, lateral alignment, risk budget and shared drift stress are study assumptions. Wilson intervals describe a fraction among accepted layouts. An empty fraction denotes zero coverage. All new numbers come from the finite graph. The paper does not include physical locomotion or hardware measurements.

For the public planning baseline, use the planning-only baseline-cp311-linux-x86_64.lock in a separate CPython 3.11.9 environment. Run the original checkout's `python run.py` to regenerate its 120 planning rows. The provided locks contain exact hashes of the NumPy distribution used by each numerical workflow.
