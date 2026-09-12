"""사주팔자 계산 엔진 — fate-js src/engine.ts 1:1 미러링."""

import json
import math
import os
from bisect import bisect_right

# ── 절기 데이터 ────────────────────────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "jieqi.json"), encoding="utf-8") as _f:
    _jieqi = json.load(_f)

jie_sec = _jieqi["sec"]      # true-UTC epoch seconds
jie_month = _jieqi["month"]  # 절기 순서(monthSeq)
jie_year = _jieqi["year"]

# ── 상수 ──────────────────────────────────────────────────────────────────────
BASE_ORD = 693626   # 1900-01-31 ordinal (甲辰日 기준일)
EPOCH_ORD = 719163  # 1970-01-01 ordinal (Unix epoch)
BASE_GAN = 0
BASE_ZHI = 4

# 월간(月干) 기준: 寅月 시작 천간 (연간 기준)
YIN_MONTH_GAN = (2, 4, 6, 8, 0, 2, 4, 6, 8, 0)
# 절기 순서 → 월지(月支) 인덱스
JIE_TO_MONTH_ZHI = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
# 寅月(mi=2) 기준 오프셋
JIE_TO_MONTH_OFFSET = (8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
# 일간(日干) → 시간(時干) 시작 인덱스
DAY_GAN_TO_HOUR_BASE = (0, 2, 4, 6, 8, 0, 2, 4, 6, 8)


def _mod(x: int, n: int) -> int:
    return ((x % n) + n) % n


def search_sorted_right(arr, val) -> int:
    """arr에서 val을 초과하는 첫 인덱스 (val 이하인 마지막 위치 + 1)."""
    return bisect_right(arr, val)


def bazi_vectorized(date_ord: int, local_hour: float, utc_sec: float) -> dict:
    """연·월·일·시 사주의 천간·지지 인덱스. fate-js baziVectorized 와 동일."""
    # ── 일주(日柱) ──
    diff = date_ord - BASE_ORD
    day_gan = _mod(BASE_GAN + diff, 10)
    day_zhi = _mod(BASE_ZHI + diff, 12)

    # ── 시주(時柱) ── 로컬 진태양시. 子時(23시)는 다음 날 일간(야자시).
    next_day = local_hour >= 23
    hour_zhi = 0 if next_day else _mod(math.floor((local_hour + 1) / 2), 12)
    day_gan_for_hour = _mod(day_gan + 1, 10) if next_day else day_gan
    hour_gan = _mod(DAY_GAN_TO_HOUR_BASE[day_gan_for_hour] + hour_zhi, 10)

    # ── 절기 탐색 ── 출생 절대순간(UTC) vs 절기 UTC.
    if not math.isfinite(utc_sec) or utc_sec < jie_sec[0] or utc_sec >= jie_sec[-1]:
        raise ValueError(
            f"절기 데이터 범위 밖이거나 유효하지 않은 시각입니다(utcSec={utc_sec}). "
            "이 라이브러리는 절기 테이블이 덮는 기간(대략 1799-01 ~ 2200-11)의 "
            "유한한 날짜/시각만 지원합니다."
        )
    pos = search_sorted_right(jie_sec, utc_sec) - 1

    month_seq = jie_month[pos]
    jy = jie_year[pos]
    yg_base = _mod(jy - 4, 10)

    # ── 연주(年柱) ── 입춘(mi=2) 기준, 大雪(0)·小寒(1)은 전년도
    year_stem = _mod(yg_base - 1, 10) if month_seq < 2 else yg_base

    # ── 월주(月柱) ──
    month_gan = _mod(YIN_MONTH_GAN[yg_base] + JIE_TO_MONTH_OFFSET[month_seq], 10)
    month_zhi = JIE_TO_MONTH_ZHI[month_seq]

    # ── 연지(年支) ──
    year_zhi_base = _mod(jy - 4, 12)
    year_zhi = _mod(year_zhi_base - 1, 12) if month_seq < 2 else year_zhi_base

    return {
        "year": {"stemIdx": year_stem, "branchIdx": year_zhi},
        "month": {"stemIdx": month_gan, "branchIdx": month_zhi},
        "day": {"stemIdx": day_gan, "branchIdx": day_zhi},
        "hour": {"stemIdx": hour_gan, "branchIdx": hour_zhi},
    }
