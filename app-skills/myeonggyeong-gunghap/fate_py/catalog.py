"""사주 카탈로그 — fate-js src/catalog.ts 1:1 미러링.

catalog(yearStart, yearEnd, utcOffsetMinutes, hours?). TypedArray 대신 plain int 리스트 반환.
"""

from .engine import EPOCH_ORD, bazi_vectorized
from .date_util import to_ordinal, from_ordinal

TIME_SLOTS = (23, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21)


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def catalog(year_start, year_end, utc_offset_minutes, hours=None):
    """연도 범위와 (선택적) 시각 목록으로 사주 카탈로그를 생성한다."""
    if hours is None:
        hours = TIME_SLOTS
    if not _is_int(year_start) or not _is_int(year_end):
        raise ValueError(f"yearStart·yearEnd는 정수여야 합니다: {year_start}, {year_end}")
    if year_start < 1 or year_end < 1:
        raise ValueError(f"연도는 1 이상이어야 합니다: {year_start}, {year_end}")
    if year_start > year_end:
        raise ValueError(f"yearStart는 yearEnd 이하여야 합니다: {year_start} > {year_end}")
    if not _is_int(utc_offset_minutes) or utc_offset_minutes < -720 or utc_offset_minutes > 840:
        raise ValueError(
            f"utcOffsetMinutes는 −720~840 사이 정수여야 합니다(필수, 암묵 기본값 없음): {utc_offset_minutes}"
        )
    for h in hours:
        if not _is_int(h) or h < 0 or h > 23:
            raise ValueError(f"hours 원소는 0–23 정수여야 합니다: {h}")

    start_ord = to_ordinal(year_start, 1, 1)
    end_ord = to_ordinal(year_end + 1, 1, 1)  # exclusive

    offset_sec = utc_offset_minutes * 60

    total_days = end_ord - start_ord
    n = total_days * len(hours)

    years_arr = [0] * n
    months_arr = [0] * n
    days_arr = [0] * n
    hours_arr = [0] * n
    slot_index = [0] * n
    stems_arr = [0] * (n * 4)
    branches_arr = [0] * (n * 4)

    row = 0
    for ord_ in range(start_ord, end_ord):
        ymd = from_ordinal(ord_)
        year, month, day = ymd["year"], ymd["month"], ymd["day"]
        for si in range(len(hours)):
            h = hours[si]
            utc_sec = (ord_ - EPOCH_ORD) * 86400 + h * 3600 - offset_sec
            idx = bazi_vectorized(ord_, h, utc_sec)

            years_arr[row] = year
            months_arr[row] = month
            days_arr[row] = day
            hours_arr[row] = h
            slot_index[row] = si

            base = row * 4
            stems_arr[base] = idx["year"]["stemIdx"]
            stems_arr[base + 1] = idx["month"]["stemIdx"]
            stems_arr[base + 2] = idx["day"]["stemIdx"]
            stems_arr[base + 3] = idx["hour"]["stemIdx"]

            branches_arr[base] = idx["year"]["branchIdx"]
            branches_arr[base + 1] = idx["month"]["branchIdx"]
            branches_arr[base + 2] = idx["day"]["branchIdx"]
            branches_arr[base + 3] = idx["hour"]["branchIdx"]

            row += 1

    return {
        "years": years_arr,
        "months": months_arr,
        "days": days_arr,
        "hours": hours_arr,
        "slotIndex": slot_index,
        "stems": stems_arr,
        "branches": branches_arr,
    }
