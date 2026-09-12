"""대운(大運)·세운(歲運) 계산 — fate-js src/daeun.ts 1:1 미러링."""

from .bazi import bazi
from .constants import BRANCH_INDEX, BRANCHES, STEM_INDEX, STEMS
from .engine import EPOCH_ORD, jie_sec, search_sorted_right
from .date_util import to_ordinal
from .tz import resolve_utc_offset_minutes
from .validate import assert_valid_birth_input


def _birth_utc_sec(inp: dict) -> float:
    year = inp["year"]
    month = inp["month"]
    day = inp["day"]
    std_hour = inp.get("hour") or 0
    std_minute = inp.get("minute") or 0
    if inp.get("utcOffsetMinutes") is not None:
        offset_min = inp["utcOffsetMinutes"]
    else:
        offset_min = resolve_utc_offset_minutes(
            inp["timezone"], year, month, day, std_hour, std_minute,
        )
    return (to_ordinal(year, month, day) - EPOCH_ORD) * 86400 + std_hour * 3600 + std_minute * 60 - offset_min * 60


def daeun(inp: dict, count: int = 10) -> dict:
    """대운(大運) 계산. inp = bazi 입력 + gender('male'|'female')."""
    assert_valid_birth_input(inp)
    gender = inp.get("gender")
    if gender != "male" and gender != "female":
        raise TypeError(f"gender는 'male' | 'female'이어야 합니다: {gender!r}")

    chart = bazi(inp)
    year_stem_idx = STEM_INDEX[chart["year"]["stem"]]
    month_stem_idx = STEM_INDEX[chart["month"]["stem"]]
    month_branch_idx = BRANCH_INDEX[chart["month"]["branch"]]

    yang_year = year_stem_idx % 2 == 0
    forward = yang_year == (gender == "male")

    utc_sec = _birth_utc_sec(inp)
    if not _finite(utc_sec) or utc_sec < jie_sec[0] or utc_sec >= jie_sec[-1]:
        raise ValueError(f"절기 데이터 범위 밖이거나 유효하지 않은 시각입니다(utcSec={utc_sec}).")
    pos = search_sorted_right(jie_sec, utc_sec) - 1
    boundary_sec = jie_sec[pos + 1] if forward else jie_sec[pos]
    boundary_days = abs(boundary_sec - utc_sec) / 86400
    start_age = boundary_days / 3

    step = 1 if forward else -1
    pillars = []
    for i in range(1, count + 1):
        stem_idx = (((month_stem_idx + step * i) % 10) + 10) % 10
        branch_idx = (((month_branch_idx + step * i) % 12) + 12) % 12
        age = start_age + 10 * (i - 1)
        import math
        pillars.append({
            "order": i,
            "startAge": age,
            "startYear": inp["year"] + math.floor(age),
            "stem": STEMS[stem_idx],
            "branch": BRANCHES[branch_idx],
        })

    return {
        "forward": forward,
        "startAge": start_age,
        "boundaryDays": boundary_days,
        "pillars": pillars,
    }


def seun(start_year: int, count: int = 5) -> list:
    """세운(歲運) — 연도별 간지. 1984 = 甲子 기준."""
    out = []
    for y in range(start_year, start_year + count):
        out.append({
            "year": y,
            "stem": STEMS[(((y - 4) % 10) + 10) % 10],
            "branch": BRANCHES[(((y - 4) % 12) + 12) % 12],
        })
    return out


def _finite(x) -> bool:
    return x == x and x not in (float("inf"), float("-inf"))
