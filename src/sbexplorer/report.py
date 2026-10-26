"""Generate a match report: summary table, shot maps and passing networks.

    python -m sbexplorer.report --list --competition 43 --season 3
    python -m sbexplorer.report --match-id 8658 --out docs
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .data import load_events, load_matches
from .passing import passing_network, plot_passing_network
from .shots import get_shots, plot_shot_map
from .summary import match_summary

COLORS = ["#d62728", "#1f77b4"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match-id", type=int)
    ap.add_argument("--list", action="store_true", help="list matches of a competition season")
    ap.add_argument("--competition", type=int, default=43)
    ap.add_argument("--season", type=int, default=3)
    ap.add_argument("--out", default="docs")
    a = ap.parse_args(argv)

    if a.list or a.match_id is None:
        m = load_matches(a.competition, a.season)
        print(m[["match_id", "match_date", "home_team", "away_team", "home_score", "away_score"]]
              .to_string(index=False))
        return

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ev = load_events(a.match_id)
    teams = list(ev["team"].dropna().unique())
    summary = match_summary(ev)
    (out / "summary.md").write_text(summary.to_markdown() + "\n")
    print(summary.to_string())

    shots = get_shots(ev)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, t, c in zip(axes, teams, COLORS):
        plot_shot_map(shots, t, ax=ax, color=c)
    fig.savefig(out / "shot_maps.png", dpi=130, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, t, c in zip(axes, teams, COLORS):
        nodes, edges = passing_network(ev, t)
        plot_passing_network(nodes, edges, ax=ax, color=c, title=f"{t}: passing network (until first sub)")
    fig.savefig(out / "passing_networks.png", dpi=130, bbox_inches="tight"); plt.close(fig)
    print("wrote", sorted(p.name for p in out.iterdir()))


if __name__ == "__main__":
    main()
