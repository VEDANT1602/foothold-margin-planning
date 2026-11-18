"""Rebuild the published figure from this repository's results.csv."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
TEAL, ORANGE, NAVY, SMOKE = "#006b68", "#ab4b26", "#223c57", "#717d87"
plt.rcParams.update({"font.size":9.5, "axes.spines.top":False, "axes.spines.right":False,
                     "figure.dpi":130, "savefig.dpi":250, "font.family":"DejaVu Sans"})


def read_results():
    with (ROOT / "results.csv").open(encoding="utf8", newline="") as stream:
        return list(csv.DictReader(stream))


def save_figure(fig):
    fig.tight_layout(pad=0.7)
    fig.savefig(ROOT / "figure.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def footholds():
    tab = [r for r in read_results() if r["split"]=="pinch_test" and r["correlation"]=="independent"
           and float(r["error_scale"])==1 and r["margin_mm"].isdigit()]
    tab.sort(key=lambda r:int(r["margin_mm"]))
    m = [int(r["margin_mm"]) for r in tab]
    fig,ax=plt.subplots(figsize=(6.25,2.5))
    for field,label,color,mark in [("accepted","Planner returned a route",NAVY,"o"),
            ("valid_accepted","Returned route fit",TEAL,"s"),("rejected_feasible","Feasible route declined",ORANGE,"^")]:
        ax.plot(m,[int(r[field]) for r in tab],label=label,color=color,marker=mark,ms=3.5)
    ax.set(xlabel="Required edge margin (mm)",ylabel="Layouts (of 1,400)",xticks=m)
    ax.legend(frameon=False,fontsize=8,loc="best")
    save_figure(fig)


if __name__ == "__main__":
    footholds()
