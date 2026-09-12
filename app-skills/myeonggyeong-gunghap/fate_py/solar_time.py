"""진태양시(眞太陽時) 보정 — fate-js src/solar-time.ts 1:1 미러링."""

import math

from .date_util import to_ordinal


def equation_of_time(year: int, month: int, day: int) -> float:
    """균시차(분). 양수 = 실제 태양시가 평균시보다 빠름. NOAA 근사식."""
    day_of_year = to_ordinal(year, month, day) - to_ordinal(year, 1, 1) + 1
    b = (2 * math.pi * (day_of_year - 81)) / 364
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def solar_correction_minutes(
    year: int,
    month: int,
    day: int,
    longitude: float,
    standard_meridian: float,
    include_eot: bool,
) -> float:
    """표준시 → 진태양시 보정량(분). 시계 시각에 더하면 진태양시."""
    longitude_min = (longitude - standard_meridian) * 4  # 1° = 4분
    eot = equation_of_time(year, month, day) if include_eot else 0
    return longitude_min + eot
