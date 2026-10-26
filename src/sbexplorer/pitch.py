"""Draw a football pitch with standard markings on a matplotlib axis."""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle


def draw_pitch(ax=None, length: float = 105.0, width: float = 68.0,
               line_color: str = "#2b2b2b", pitch_color: str = "#f4f7f2",
               invert_y: bool = True, lw: float = 1.2):
    """Draw a pitch of ``length`` x ``width`` and return the axis.

    Markings are scaled from real-world dimensions (metres on a 105 x 68 pitch),
    so the same function works for 105x68 (Metrica, in metres) and for
    120x80 (StatsBomb, in yards).

    Parameters
    ----------
    invert_y : if True, y = 0 is at the top (matches Metrica and StatsBomb data).
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 6))
    sx, sy = length / 105.0, width / 68.0
    kw = dict(fill=False, ec=line_color, lw=lw, zorder=2)

    ax.add_patch(Rectangle((0, 0), length, width, fc=pitch_color, ec=line_color, lw=lw, zorder=1))
    ax.plot([length / 2] * 2, [0, width], c=line_color, lw=lw, zorder=2)
    ax.add_patch(Circle((length / 2, width / 2), 9.15 * sx, **kw))
    ax.scatter([length / 2], [width / 2], c=line_color, s=8, zorder=2)

    pa_d, pa_w = 16.5 * sx, 40.32 * sy          # penalty area
    ga_d, ga_w = 5.5 * sx, 18.32 * sy           # six-yard box
    spot = 11.0 * sx
    for side in (0, 1):
        x0 = 0 if side == 0 else length
        sgn = 1 if side == 0 else -1
        ax.add_patch(Rectangle((x0 if side == 0 else x0 - pa_d, (width - pa_w) / 2), pa_d, pa_w, **kw))
        ax.add_patch(Rectangle((x0 if side == 0 else x0 - ga_d, (width - ga_w) / 2), ga_d, ga_w, **kw))
        ax.scatter([x0 + sgn * spot], [width / 2], c=line_color, s=8, zorder=2)
        # penalty arc ("D")
        ax.add_patch(Arc((x0 + sgn * spot, width / 2), 2 * 9.15 * sx, 2 * 9.15 * sy,
                         theta1=-53 if side == 0 else 127, theta2=53 if side == 0 else 233,
                         ec=line_color, lw=lw, zorder=2))
        # goal
        gw = 7.32 * sy
        ax.add_patch(Rectangle((x0 - (2 * sx if side == 0 else 0), (width - gw) / 2),
                               2 * sx, gw, fill=False, ec=line_color, lw=lw, zorder=2))

    pad = 3
    ax.set_xlim(-pad, length + pad)
    ax.set_ylim((width + pad, -pad) if invert_y else (-pad, width + pad))
    ax.set_aspect("equal")
    ax.axis("off")
    return ax
