"""ordinal 날짜 유틸 — fate-js src/date-util.ts 1:1 미러링.

Proleptic Gregorian Calendar 기준. 1년 1월 1일 = ordinal 1.
"""

_DAYS_BEFORE_MONTH = [0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


def _days_before_year(y: int) -> int:
    ym1 = y - 1
    return 365 * ym1 + (ym1 // 4) - (ym1 // 100) + (ym1 // 400)


def _is_leap(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


def _days_before_month(year: int, month: int) -> int:
    base = _DAYS_BEFORE_MONTH[month] if 0 <= month < len(_DAYS_BEFORE_MONTH) else 0
    return base + (1 if (month > 2 and _is_leap(year)) else 0)


def to_ordinal(year: int, month: int, day: int) -> int:
    """(year, month, day) → ordinal. 1년 1월 1일 = 1."""
    return _days_before_year(year) + _days_before_month(year, month) + day


def from_ordinal(ord_: int) -> dict:
    """ordinal → {year, month, day}. 1년 1월 1일 = 1. (Meeus ch.7)"""
    n = ord_ - 1  # 0-based days since 0001-01-01
    n400 = n // 146097
    n -= n400 * 146097
    n100 = min(n // 36524, 3)
    n -= n100 * 36524
    n4 = n // 1461
    n -= n4 * 1461
    n1 = min(n // 365, 3)
    n -= n1 * 365

    year = n400 * 400 + n100 * 100 + n4 * 4 + n1 + 1
    leap = 1 if _is_leap(year) else 0
    month = 1
    while month < 12:
        nxt = (_DAYS_BEFORE_MONTH[month + 1] if month + 1 < len(_DAYS_BEFORE_MONTH) else 0) + (leap if month >= 2 else 0)
        if n < nxt:
            break
        month += 1
    day = n - _days_before_month(year, month) + 1
    return {"year": year, "month": month, "day": day}
