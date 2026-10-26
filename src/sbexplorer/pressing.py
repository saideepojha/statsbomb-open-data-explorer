"""Pressing intensity (PPDA)."""
from __future__ import annotations

import pandas as pd


def ppda(events: pd.DataFrame, team: str) -> float:
    """Passes Allowed Per Defensive Action for ``team`` (lower = more pressing).

    PPDA = opponent passes in the opponent's own 60% of the pitch
           / team's defensive actions in that same zone.

    StatsBomb coordinates: every team attacks towards x = 120, so the opponent's own
    60% is x < 72 for their passes and x >= 48 for our defensive actions.
    Defensive actions here are tackles, interceptions and fouls committed.
    This is a common approximation; providers differ slightly in what they count.
    """
    opp = events[(events["team"] != team) & (events["type"] == "Pass") & (events["x"] < 72)]
    mine = events[(events["team"] == team) & (events["x"] >= 48)]
    tackles = (mine["type"] == "Duel") & (mine.get("duel_type", pd.Series(index=mine.index, dtype=object)) == "Tackle")
    actions = tackles | mine["type"].isin(["Interception", "Foul Committed"])
    n = int(actions.sum())
    return float("nan") if n == 0 else len(opp) / n
