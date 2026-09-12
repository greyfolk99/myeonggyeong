"""사주팔자 사주(四柱) 계산 — fate-js src/bazi.ts 1:1 미러링."""

from .config import get_solar_config
from .constants import BRANCHES, STEMS
from .engine import EPOCH_ORD, bazi_vectorized
from .date_util import to_ordinal
from .solar_time import solar_correction_minutes
from .tz import resolve_utc_offset_minutes
from .validate import assert_valid_birth_input


def bazi(inp: dict) -> dict:
    """생년월일시 dict → 사주 dict {year,month,day,hour}. hour 미지정이면 hour=None.

    inp keys (fate-js BirthInput 과 동일): year, month, day, hour?, minute?,
    timeBasis?('standard'|'solar'), longitude?, timezone?, utcOffsetMinutes?
    (timezone 또는 utcOffsetMinutes 중 최소 하나 필수)
    """
    assert_valid_birth_input(inp)
    year = inp["year"]
    month = inp["month"]
    day = inp["day"]
    hour = inp.get("hour")
    minute = inp.get("minute")
    has_time = hour is not None
    cfg = get_solar_config()
    time_basis = inp.get("timeBasis")
    apply_solar = (time_basis == "solar") if time_basis else cfg["applySolarTime"]

    date_ord = to_ordinal(year, month, day)  # 일주: 로컬 civil 날짜
    std_hour = hour if hour is not None else 0
    std_minute = minute if minute is not None else 0

    # ── 절기용 절대순간(UTC) ──
    if inp.get("utcOffsetMinutes") is not None:
        offset_min = inp["utcOffsetMinutes"]
    else:
        offset_min = resolve_utc_offset_minutes(
            inp["timezone"], year, month, day, std_hour, std_minute,
        )
    utc_sec = (date_ord - EPOCH_ORD) * 86400 + std_hour * 3600 + std_minute * 60 - offset_min * 60

    # ── 시주용 로컬 진태양시 시각 ──
    local_hour = std_hour + std_minute / 60
    if has_time and apply_solar:
        longitude = inp.get("longitude")
        if longitude is None:
            longitude = cfg["defaultLongitude"]
        corr = solar_correction_minutes(
            year, month, day, longitude, cfg["standardMeridian"], cfg["applyEot"],
        )
        local_hour += corr / 60
        local_hour = ((local_hour % 24) + 24) % 24

    idx = bazi_vectorized(date_ord, local_hour if has_time else 0, utc_sec)
    return {
        "year": {"stem": STEMS[idx["year"]["stemIdx"]], "branch": BRANCHES[idx["year"]["branchIdx"]]},
        "month": {"stem": STEMS[idx["month"]["stemIdx"]], "branch": BRANCHES[idx["month"]["branchIdx"]]},
        "day": {"stem": STEMS[idx["day"]["stemIdx"]], "branch": BRANCHES[idx["day"]["branchIdx"]]},
        "hour": (
            {"stem": STEMS[idx["hour"]["stemIdx"]], "branch": BRANCHES[idx["hour"]["branchIdx"]]}
            if has_time else None
        ),
    }
