"""Plot the effect of demanding complete laser evidence on the same routes."""

from pathlib import Path
import csv
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
with (root / "summary.csv").open() as f:
    row = next(
        r
        for r in csv.DictReader(f)
        if int(r["cells_required"]) == 5
        and float(r["roughness_m"]) == 0.10
        and r["policy"] == "graph"
    )
groups = [int(row[k]) for k in ["validated", "contradicted", "unresolved"]]
strict = [int(row[k]) for k in ["strict_confirmed", "strict_contradicted", "strict_unresolved"]]
fig, ax = plt.subplots(figsize=(8, 2), layout="constrained")
colors = ["#2b716d", "#a03f31", "#bec8cf"]
left = [0, 0]
for i, (label, color) in enumerate(zip(["Agrees", "Contradicts", "Unresolved"], colors)):
    values = [groups[i], strict[i]]
    ax.barh([1, 0], values, left=left, color=color, label=label, height=0.48)
    for j, (width, start) in enumerate(zip(values, left)):
        if width > 35:
            ax.text(
                start + width / 2,
                1 - j,
                str(width),
                ha="center",
                va="center",
                color="white" if i == 0 else "#26343b",
                fontsize=10,
            )
    left = [start + width for start, width in zip(left, values)]
ax.set_yticks([1, 0], ["≥5 laser cells", "All 9 laser cells"])
ax.set_xlim(0, 468)
ax.set_xticks([0, 100, 200, 300, 400, 468])
ax.set_xlabel("Paths from the same 468 stereo proposals")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(ncols=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01), fontsize=9)
fig.savefig(root / "laser-coverage.png", dpi=220)
