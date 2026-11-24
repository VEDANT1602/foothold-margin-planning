"""Recompute the published terrain tables from the released per-scan counts."""
import argparse
import csv
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
FIELDS = ('selected', 'supported', 'contradicted', 'unresolved')
FIVE_CELL = {
    'quadruped': ((190, 104, 13, 73), (190, 12, 1, 177), 9262, 39.6),
    'online': ((194, 77, 49, 68), (194, 23, 21, 150), 6966, 266.5),
    'online_10s': ((192, 78, 47, 67), (192, 26, 20, 146), 6813, 318.1),
}
CONDITIONS = {(3, 3), (3, 9), (5, 5), (5, 9), (7, 7), (7, 9), (9, 9)}


def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def check(directory):
    selected_scans = {row['scan'] for row in read(HERE / 'quadruped_input_manifest.csv')}
    assert len(selected_scans) == 30
    for prefix, (partial, full, cell_count, gap_mm) in FIVE_CELL.items():
        frames = read(directory / f'{prefix}_frames.csv')
        assert len(frames) == 30 and {row['scan'] for row in frames} == selected_scans
        assert sum(int(row['common_cells']) for row in frames) == cell_count
        gap = median(1000 * float(row['median_absolute_height_gap_m']) for row in frames)
        assert round(gap, 1) == gap_mm
        if prefix != 'quadruped':
            assert min(float(row['seconds_since_anchor']) for row in frames) > 71
        by_condition = {condition: {} for condition in CONDITIONS}
        for row in read(directory / f'{prefix}_footprints.csv'):
            counts = tuple(int(row[key]) for key in FIELDS)
            assert min(counts) >= 0 and counts[0] == sum(counts[1:])
            assert int(row['candidate_tiles']) == 340
            condition = int(row['required_robot']), int(row['required_survey'])
            bucket = by_condition[condition]
            assert row['scan'] not in bucket
            bucket[row['scan']] = counts
        sums = {}
        for condition, bucket in by_condition.items():
            assert set(bucket) == selected_scans
            sums[condition] = tuple(map(sum, zip(*bucket.values())))
        for scan in selected_scans:
            assert by_condition[5, 5][scan][0] == by_condition[5, 9][scan][0]
        assert sums[5, 5] == partial and sums[5, 9] == full
        if prefix == 'quadruped':
            assert sums[3, 3] == (584, 427, 85, 72)
            assert sums[7, 7] == (14, 4, 0, 10)
            assert sums[9, 9] == (0, 0, 0, 0)
        counts = list(by_condition[5, 5].values())
        selected, supported, contradicted, unresolved = partial
        assessable = supported + contradicted
        scan_count = sum(row[2] > 0 for row in counts)
        omit_one = [(contradicted - row[2]) / (selected - row[0]) for row in counts]
        print(f'{prefix}: {assessable}/{selected} assessable, {contradicted}/{assessable} '
              f'contradicted among assessable, {scan_count}/30 scans with contradictions, '
              f'leave-one-scan contradiction fraction among all selections '
              f'{min(omit_one):.1%} to {max(omit_one):.1%}')
        if prefix in ('quadruped', 'online'):
            expected_counts = (117, 7) if prefix == 'quadruped' else (126, 20)
            assert (assessable, scan_count) == expected_counts
        print(f'{prefix} — selected, supported, contradicted, unresolved: {partial}; '
              f'complete survey requirement: {full}; common cells: {cell_count:,}; '
              f'median gap: {gap:.1f} mm')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, nargs='?', default=HERE)
    check(parser.parse_args().directory)
