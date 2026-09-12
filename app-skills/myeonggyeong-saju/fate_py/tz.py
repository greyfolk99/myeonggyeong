"""IANA 타임존 리졸버 — fate-js src/timezone.ts 1:1 미러링.

JS는 Intl.DateTimeFormat 의 tzdata 를 쓴다. 파이썬은 표준 zoneinfo(동일 IANA tzdb)를
써서 같은 알고리즘(고정점 2회 반복)으로 로컬 벽시계 → UTC 오프셋(분)을 구한다.
반올림은 JS Math.round(=floor(x+0.5)) 와 동일하게 맞춘다.
"""

import math
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_zi_cache: dict = {}


def _zone(tzname: str) -> ZoneInfo:
    z = _zi_cache.get(tzname)
    if z is None:
        try:
            z = ZoneInfo(tzname)
        except (ZoneInfoNotFoundError, ValueError, Exception):
            raise ValueError(f'유효한 IANA 타임존이 아닙니다: "{tzname}" (예: "Asia/Seoul")')
        _zi_cache[tzname] = z
    return z


def _jround(x: float) -> int:
    """JS Math.round: 반올림 .5는 +무한대 방향."""
    return math.floor(x + 0.5)


def _zone_offset_minutes_at(tzname: str, utc_sec: float) -> int:
    """특정 절대순간(UTC epoch 초)에 그 존이 갖는 오프셋(분)."""
    dt = datetime.fromtimestamp(utc_sec, tz=_zone(tzname))
    return _jround(dt.utcoffset().total_seconds() / 60)


def resolve_utc_offset_minutes(
    tzname: str, year: int, month: int, day: int, hour: int = 0, minute: int = 0,
) -> int:
    """IANA 타임존 + 로컬 벽시계 → UTC 오프셋(분, 동쪽 +). 고정점 2회."""
    # 벽시계 시각을 UTC로 해석한 절대순간(초). JS의 setUTCFullYear/... 와 동일.
    local_as_utc = datetime(
        year, month, day, hour, minute, 0, tzinfo=ZoneInfo("UTC"),
    ).timestamp()
    first = _zone_offset_minutes_at(tzname, local_as_utc)
    return _zone_offset_minutes_at(tzname, local_as_utc - first * 60)
