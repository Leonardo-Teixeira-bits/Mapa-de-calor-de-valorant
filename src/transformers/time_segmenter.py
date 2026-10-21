"""Dynamic temporal segmentation of round events into Early, Mid, and Late phases."""

from __future__ import annotations
from typing import Optional, Literal

DEFAULT_ROUND_DURATION_MS = 100000  # 100 seconds standard competitive round


def classify_round_phase(
    time_millis: int,
    round_duration_millis: Optional[int] = None
) -> Literal["Early", "Mid", "Late"]:
    """
    Classifies a kill event into Early, Mid, or Late round phase based on
    dynamic proportions of the round's actual duration.

    - Early: 0 <= t < 1/3 * T_max
    - Mid:   1/3 * T_max <= t < 2/3 * T_max
    - Late:  t >= 2/3 * T_max
    """
    duration = round_duration_millis if (round_duration_millis and round_duration_millis > 0) else DEFAULT_ROUND_DURATION_MS
    t = max(0, time_millis)

    one_third = duration / 3.0
    two_thirds = (duration * 2.0) / 3.0

    if t < one_third:
        return "Early"
    elif t < two_thirds:
        return "Mid"
    else:
        return "Late"
