#!/usr/bin/env python3
"""명경(明鏡) 사주 계산 러너 — 동봉된 fate_py(순수 파이썬)로 사주 시트를 뽑는다.

인터넷·npm 없는 파이썬 샌드박스(ChatGPT·Claude 앱)에서도 그대로 실행된다.
계산만 한다 — 해석/살붙이기는 SKILL.md 지침과 reference/interpretation-guide.md 를 따른다.

사용:
  python bin/saju.py --year 1992 --month 8 --day 4 --hour 3 --minute 30 \
      --gender female --name 지민 [--timezone Asia/Seoul | --offset 540] [--no-solar]
시간 모름:
  python bin/saju.py --year 1992 --month 8 --day 4 --gender male
출력: 사람이 읽는 요약 + '===JSON===' 뒤에 baziSheet 팩트(JSON, 해석의 근거).
"""
import argparse
import json
import os
import sys

# 동봉 fate_py 를 import 경로에 추가(스킬 루트 = 이 파일의 상위 디렉토리).
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

from fate_py import bazi, bazi_sheet, format_bazi_sheet, daeun, seun  # noqa: E402


def build_input(a):
    inp = {"year": a.year, "month": a.month, "day": a.day}
    if a.hour is not None:
        inp["hour"] = a.hour
        if a.minute is not None:
            inp["minute"] = a.minute
    if a.no_solar:
        inp["timeBasis"] = "standard"
    if a.longitude is not None:
        inp["longitude"] = a.longitude
    if a.offset is not None:
        inp["utcOffsetMinutes"] = a.offset
    else:
        inp["timezone"] = a.timezone
    return inp


def with_tz_fallback(inp, gender, offset_fallback):
    """timezone 해석이 안 되는 최소 샌드박스면 오프셋으로 폴백(현대 날짜 근사)."""
    try:
        return bazi(inp), inp, None
    except Exception as e:
        if "timezone" in inp and offset_fallback is not None:
            inp2 = {k: v for k, v in inp.items() if k != "timezone"}
            inp2["utcOffsetMinutes"] = offset_fallback
            return bazi(inp2), inp2, f"(참고: 이 환경에 tz 데이터가 없어 오프셋 {offset_fallback}분으로 계산)"
        raise e


def main():
    p = argparse.ArgumentParser(description="명경 사주 계산")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--month", type=int, required=True)
    p.add_argument("--day", type=int, required=True)
    p.add_argument("--hour", type=int, default=None)
    p.add_argument("--minute", type=int, default=None)
    p.add_argument("--gender", choices=["male", "female"], required=True)
    p.add_argument("--name", default="본인")
    p.add_argument("--timezone", default="Asia/Seoul")
    p.add_argument("--offset", type=int, default=None, help="UTC offset(분). timezone 대신 사용.")
    p.add_argument("--longitude", type=float, default=None)
    p.add_argument("--no-solar", action="store_true", help="진태양시 보정 끄기")
    p.add_argument("--daeun", type=int, default=8, help="대운 개수(시주 있을 때만 정확)")
    a = p.parse_args()

    inp = build_input(a)
    default_offset = 540 if a.timezone == "Asia/Seoul" else None
    chart, used, note = with_tz_fallback(inp, a.gender, default_offset)

    has_hour = chart.get("hour") is not None
    out = {"name": a.name, "gender": a.gender, "hasHour": has_hour, "bazi": chart}

    print(f"■ {a.name} — {a.year}-{a.month:02d}-{a.day:02d}"
          + (f" {a.hour:02d}:{(a.minute or 0):02d}" if has_hour else " (시간 모름)")
          + f" · {'남' if a.gender=='male' else '여'}")
    if note:
        print(note)

    if has_hour:
        sheet = bazi_sheet({"bazi": chart, "gender": a.gender})
        out["baziSheet"] = sheet
        print()
        print(format_bazi_sheet(sheet, a.name))
        # 대운(시주 있을 때만 대운수 정확)
        try:
            du = daeun({**used, "gender": a.gender}, a.daeun)
            out["daeun"] = du
            arrow = "순행" if du["forward"] else "역행"
            print(f"\n【대운(大運)】 {arrow} · 대운수 {du['startAge']:.1f}세")
            print("  " + "  ".join(f"{d['startYear']}({d['startAge']:.0f}세) {d['stem']}{d['branch']}" for d in du["pillars"]))
        except Exception as e:
            out["daeunErr"] = str(e)
    else:
        b = chart
        print("\n【사주(시주 없음)】")
        print(f"  년 {b['year']['stem']}{b['year']['branch']}  월 {b['month']['stem']}{b['month']['branch']}  일 {b['day']['stem']}{b['day']['branch']}")
        print("  ※ 시주 미상 — 시주·시주 기반 항목(시지 신살·정확한 대운수)은 계산하지 않음")

    print("\n===JSON===")
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
