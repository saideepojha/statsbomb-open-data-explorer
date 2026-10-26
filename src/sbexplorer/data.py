"""Thin, cached wrappers around statsbombpy (free open data, no credentials needed)."""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore", message=".*credentials.*")
from statsbombpy import sb  # noqa: E402

CACHE = Path("data/cache")


def competitions() -> pd.DataFrame:
    """All competitions/seasons available in the open data."""
    return sb.competitions()


def load_matches(competition_id: int, season_id: int) -> pd.DataFrame:
    """Matches of one competition season (e.g. 43, 3 = FIFA World Cup 2018)."""
    return sb.matches(competition_id=competition_id, season_id=season_id)


def load_events(match_id: int, cache: bool = True) -> pd.DataFrame:
    """All events of a match, with ``x``/``y`` columns split out of ``location``.

    Results are cached as pickles in ``data/cache`` (git-ignored).
    """
    path = CACHE / f"events_{match_id}.pkl"
    if cache and path.exists():
        return pd.read_pickle(path)
    ev = sb.events(match_id=match_id)
    ev = add_xy(ev)
    if cache:
        CACHE.mkdir(parents=True, exist_ok=True)
        ev.to_pickle(path)
    return ev


def add_xy(ev: pd.DataFrame) -> pd.DataFrame:
    """Add x, y (event location) and end_x, end_y (pass end location) columns."""
    ev = ev.copy()
    for col, (cx, cy) in {"location": ("x", "y"), "pass_end_location": ("end_x", "end_y")}.items():
        if col in ev:
            pts = ev[col].apply(lambda v: v if isinstance(v, (list, tuple)) and len(v) >= 2 else [None, None])
            ev[cx] = pts.str[0].astype(float)
            ev[cy] = pts.str[1].astype(float)
    return ev
