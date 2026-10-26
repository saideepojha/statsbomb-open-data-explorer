"""Passing networks."""
from __future__ import annotations

import pandas as pd

from .pitch import draw_pitch

PITCH = (120.0, 80.0)


def passing_network(events: pd.DataFrame, team: str, min_passes: int = 3):
    """Build a passing network for ``team`` until its first substitution.

    Returns ``(nodes, edges)``:
      nodes: index = player, columns x, y (average pass origin and receipt location),
             passes (completed passes made + received)
      edges: columns a, b, count (completed passes between the pair, both directions)
    """
    ev = events[events["team"] == team]
    subs = ev[ev["type"] == "Substitution"]
    if len(subs):
        cut = subs.sort_values("index").iloc[0]["index"]
        ev = ev[ev["index"] < cut]
    p = ev[(ev["type"] == "Pass") & ev["pass_outcome"].isna()].dropna(subset=["pass_recipient"])
    # node position = average of where a player passes from and where he receives
    made = p[["player", "x", "y"]].rename(columns={"player": "name"})
    parts = [made]
    if {"end_x", "end_y"} <= set(p.columns):
        got = p[["pass_recipient", "end_x", "end_y"]].rename(
            columns={"pass_recipient": "name", "end_x": "x", "end_y": "y"})
        parts.append(got)
    touches = pd.concat(parts)
    nodes = touches.groupby("name").agg(x=("x", "mean"), y=("y", "mean"), passes=("x", "size"))
    nodes.index.name = "player"
    pairs = p.assign(a=p[["player", "pass_recipient"]].min(axis=1),
                     b=p[["player", "pass_recipient"]].max(axis=1))
    edges = pairs.groupby(["a", "b"]).size().reset_index(name="count")
    edges = edges[edges["count"] >= min_passes]
    nodes = nodes[nodes.index.isin(set(edges["a"]) | set(edges["b"]))]
    return nodes, edges


def short_name(full: str) -> str:
    """Last name for labels; skips tiny trailing tokens (e.g. 'Lucas Hernández Pi')."""
    parts = full.split()
    if len(parts) > 1 and len(parts[-1]) <= 2:
        return parts[-2]
    return parts[-1] if parts else full


def plot_passing_network(nodes: pd.DataFrame, edges: pd.DataFrame, ax=None,
                         color: str = "#1f77b4", title: str | None = None):
    """Draw nodes (size = passes made) and edges (width = passes exchanged)."""
    ax = draw_pitch(ax, length=PITCH[0], width=PITCH[1], invert_y=True)
    mx = max(edges["count"].max(), 1) if len(edges) else 1
    for _, r in edges.iterrows():
        if r["a"] in nodes.index and r["b"] in nodes.index:
            a, b = nodes.loc[r["a"]], nodes.loc[r["b"]]
            ax.plot([a.x, b.x], [a.y, b.y], c=color, lw=0.8 + 7 * r["count"] / mx,
                    alpha=0.25 + 0.5 * r["count"] / mx, zorder=3, solid_capstyle="round")
    ax.scatter(nodes["x"], nodes["y"], s=120 + nodes["passes"] * 12, c=color, ec="white",
               lw=1.5, zorder=4)
    for name, r in nodes.iterrows():
        ax.text(r["x"], r["y"] - 4.5, short_name(name), ha="center", fontsize=7, zorder=5)
    if title:
        ax.set_title(title)
    return ax
