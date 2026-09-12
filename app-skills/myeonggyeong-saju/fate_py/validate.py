"""입력 검증 — fate-js src/validate.ts 1:1 미러링.

잘못된 날짜·시간·경도를 계산 이전에 차단한다. JS의 RangeError/Error 를
Python ValueError 로 옮긴다(메시지 동일 취지).
"""

import math

from .date_util import from_ordinal, to_ordinal


def _assert_finite_int(v, name: str) -> None:
    if not isinstance(v, int) or isinstance(v, bool) or not math.isfinite(v):
        raise ValueError(f"{name}는 유한한 정수여야 합니다: {v!r}")


def assert_longitude(v, name: str) -> None:
    """경도·표준자오선 등 각도값: −180~180 사이 유한 실수."""
    if not (isinstance(v, (int, float)) and not isinstance(v, bool)) or not math.isfinite(v) or v < -180 or v > 180:
        raise ValueError(f"{name}는 −180~180 사이 유한값이어야 합니다: {v!r}")


def assert_valid_date(year: int, month: int, day: int) -> None:
    """proleptic Gregorian 실존 날짜인지 확인(2월 30일 등 거부)."""
    _assert_finite_int(year, "year")
    _assert_finite_int(month, "month")
    _assert_finite_int(day, "day")
    if year < 1:
        raise ValueError(f"year는 1 이상이어야 합니다: {year}")
    if month < 1 or month > 12:
        raise ValueError(f"month는 1–12여야 합니다: {month}")
    if day < 1 or day > 31:
        raise ValueError(f"day는 1–31여야 합니다: {day}")
    rt = from_ordinal(to_ordinal(year, month, day))
    if rt["year"] != year or rt["month"] != month or rt["day"] != day:
        raise ValueError(f"실존하지 않는 날짜입니다: {year:04d}-{month:02d}-{day:02d}")


def assert_valid_birth_input(inp: dict) -> None:
    """출생 입력 전체 검증. fate-js assertValidBirthInput 와 동일 순서/규칙."""
    assert_valid_date(inp["year"], inp["month"], inp["day"])

    hour = inp.get("hour")
    if hour is not None:
        _assert_finite_int(hour, "hour")
        if hour < 0 or hour > 23:
            raise ValueError(f"hour는 0–23여야 합니다: {hour}")

    minute = inp.get("minute")
    if minute is not None:
        if hour is None:
            raise ValueError("minute는 hour 없이 단독으로 지정할 수 없습니다")
        _assert_finite_int(minute, "minute")
        if minute < 0 or minute > 59:
            raise ValueError(f"minute는 0–59여야 합니다: {minute}")

    longitude = inp.get("longitude")
    if longitude is not None:
        assert_longitude(longitude, "longitude")

    time_basis = inp.get("timeBasis")
    if time_basis is not None and time_basis != "standard" and time_basis != "solar":
        raise ValueError(f'timeBasis는 "standard" 또는 "solar"여야 합니다: {time_basis!r}')

    has_offset = inp.get("utcOffsetMinutes") is not None
    has_timezone = inp.get("timezone") is not None
    if not has_offset and not has_timezone:
        raise ValueError(
            "timezone(IANA, 예: 'Asia/Seoul') 또는 utcOffsetMinutes(분, DST·역사변경 포함) "
            "중 하나는 필수입니다. KST 등 암묵 가정 금지."
        )
    if has_timezone and not has_offset and (not isinstance(inp.get("timezone"), str) or len(inp["timezone"]) == 0):
        raise ValueError(f"timezone은 비어있지 않은 IANA 문자열이어야 합니다: {inp.get('timezone')!r}")
    off = inp.get("utcOffsetMinutes")
    if off is not None:
        _assert_finite_int(off, "utcOffsetMinutes")
        if off < -720 or off > 840:
            raise ValueError(f"utcOffsetMinutes는 −720~840 사이여야 합니다: {off}")
