"""Shot extraction, shot maps and xG summaries."""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from .pitch import draw_pitch

PITCH = (120.0, 80.0)  # StatsBomb coordinates (yards)


def get_shots(events: pd.DataFrame, include_shootout: bool = False) -> pd.DataFrame:
    """Return one row per shot with location, xG, outcome and shooter.

    Penalty-shootout kicks (period 5) are excluded unless ``include_shootout``.
    """
    s = events[events["type"] == "Shot"].copy()
    if not include_shootout:
        s = s[s["period"] != 5]
    cols = ["team", "player", "minute", "x", "y", "shot_statsbomb_xg", "shot_outcome",
            "shot_body_part", "shot_type"]
    s = s[[c for c in cols if c in s.columns]].rename(
        columns={"shot_statsbomb_xg": "xg", "shot_outcome": "outcome",
                 "shot_body_part": "body_part", "shot_type": "shot_type"})
    s["is_goal"] = s["outcome"].eq("Goal")
    return s.reset_index(drop=True)


def plot_shot_map(shots: pd.DataFrame, team: str, ax=None, color: str = "#d62728"):
    """Shot map for one team, attacking left to right.

    Marker size is proportional to xG; stars are goals, circles are other shots.
    """
    ax = draw_pitch(ax, length=PITCH[0], width=PITCH[1], invert_y=True)
    t = shots[shots["team"] == team]
    ax.set_xlim(PITCH[0] / 2 - 2, PITCH[0] + 3)  # attacking half
    for goal, marker in ((False, "o"), (True, "*")):
        d = t[t["is_goal"] == goal]
        ax.scatter(d["x"], d["y"], s=60 + d["xg"].fillna(0.05) * 900, c=color if goal else "none",
                   edgecolors=color, linewidths=1.6, marker=marker, alpha=0.9, zorder=4,
                   label="Goal" if goal else "No goal")
    ax.set_title(f"{team}: {len(t)} shots, {int(t['is_goal'].sum())} goals, "
                 f"xG {t['xg'].sum():.2f}", fontsize=10)
    ax.legend(loc="lower left", fontsize=8, frameon=False)
    return ax


def xg_table(shots: pd.DataFrame) -> pd.DataFrame:
    """Per-team shots, goals, xG and xG per shot."""
    g = shots.groupby("team").agg(shots=("xg", "size"), goals=("is_goal", "sum"),
                                  xg=("xg", "sum"))
    g["xg_per_shot"] = g["xg"] / g["shots"]
    return g.round(3)
