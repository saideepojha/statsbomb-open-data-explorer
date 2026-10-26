"""Offline tests with a tiny synthetic event table (no network needed)."""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import pytest

from sbexplorer.passing import passing_network, plot_passing_network, short_name
from sbexplorer.pressing import ppda
from sbexplorer.shots import get_shots, plot_shot_map, xg_table
from sbexplorer.summary import match_summary
from sbexplorer.data import add_xy


def make_events():
    rows = []
    def ev(i, type_, team, **kw):
        rows.append(dict(index=i, type=type_, team=team, period=kw.pop("period", 1), minute=i,
                         player=kw.pop("player", "P " + team),
                         x=kw.pop("x", 60.0), y=kw.pop("y", 40.0), **kw))
    # team A: 2 shots (1 goal), passes among two players, one sub late
    ev(1, "Shot", "A", x=108, y=40, shot_statsbomb_xg=0.4, shot_outcome="Goal", player="Ann Lee")
    ev(2, "Shot", "A", x=95, y=30, shot_statsbomb_xg=0.1, shot_outcome="Saved", player="Ann Lee")
    ev(3, "Shot", "A", x=110, y=40, shot_statsbomb_xg=0.7, shot_outcome="Goal", player="Pen Taker", period=5)
    for i in range(4, 10):
        ev(i, "Pass", "A", player="Ann Lee", pass_recipient="Bob Ray", pass_outcome=np.nan, x=50.0, y=30.0, end_x=70.0, end_y=30.0)
    ev(10, "Pass", "A", player="Ann Lee", pass_recipient="Bob Ray", pass_outcome="Incomplete")
    ev(20, "Substitution", "A")
    ev(21, "Pass", "A", player="Zed Q", pass_recipient="Bob Ray", pass_outcome=np.nan)
    # team B: 6 passes in own 60%, A makes tackle + interception + foul in the high zone
    for i in range(30, 36):
        ev(i, "Pass", "B", x=30.0, pass_outcome=np.nan)
    ev(40, "Duel", "A", x=70.0, duel_type="Tackle")
    ev(41, "Interception", "A", x=60.0)
    ev(42, "Foul Committed", "A", x=20.0)   # too deep: not counted
    return pd.DataFrame(rows)


def test_get_shots_excludes_shootout_and_flags_goals():
    s = get_shots(make_events())
    assert len(s) == 2 and s["is_goal"].sum() == 1
    t = xg_table(s)
    assert t.loc["A", "xg"] == pytest.approx(0.5)


def test_ppda_counts_only_high_zone_actions():
    # opponent passes in own 60%: 6 ; actions: tackle + interception = 2 -> 3.0
    assert ppda(make_events(), "A") == pytest.approx(3.0)


def test_passing_network_stops_at_first_substitution_and_filters_edges():
    nodes, edges = passing_network(make_events(), "A", min_passes=3)
    assert set(nodes.index) == {"Ann Lee", "Bob Ray"}   # Zed Q only passes after the sub
    assert edges.iloc[0]["count"] == 6                  # incomplete pass excluded


def test_match_summary_and_plots_run():
    ev = make_events()
    summ = match_summary(ev)
    assert {"shots", "xg", "passes", "ppda"} <= set(summ.columns)
    plot_shot_map(get_shots(ev), "A")
    n, e = passing_network(ev, "A")
    plot_passing_network(n, e)


def test_short_name_handles_tiny_suffix():
    assert short_name("Lucas Hernández Pi") == "Hernández"
    assert short_name("Kylian Mbappé") == "Mbappé"


def test_add_xy_splits_locations():
    df = pd.DataFrame({"location": [[10, 20], None], "pass_end_location": [[30, 40], None]})
    out = add_xy(df)
    assert out.loc[0, "x"] == 10 and out.loc[0, "end_y"] == 40 and np.isnan(out.loc[1, "x"])
