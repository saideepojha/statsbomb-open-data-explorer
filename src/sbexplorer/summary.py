"""One-table match summary."""
from __future__ import annotations

import pandas as pd

from .pressing import ppda
from .shots import get_shots, xg_table


def match_summary(events: pd.DataFrame) -> pd.DataFrame:
    """Per-team shots, goals, xG, passes, pass completion, share of passes and PPDA."""
    shots = xg_table(get_shots(events))
    p = events[events["type"] == "Pass"]
    passes = p.groupby("team").agg(passes=("type", "size"),
                                   completed=("pass_outcome", lambda s: int(s.isna().sum())))
    out = shots.join(passes, how="outer").fillna(0)
    out["pass_completion_%"] = (100 * out["completed"] / out["passes"]).round(1)
    out["pass_share_%"] = (100 * out["passes"] / out["passes"].sum()).round(1)
    out["ppda"] = [round(ppda(events, t), 2) for t in out.index]
    return out.drop(columns="completed")
