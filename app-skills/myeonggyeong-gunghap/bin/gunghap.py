#!/usr/bin/env python3
"""명경(明鏡) 궁합 계산 러너 — 동봉된 fate_py로 두 사람의 관계 시트를 뽑는다.

인터넷·npm 없는 파이썬 샌드박스(ChatGPT·Claude 앱)에서도 그대로 실행된다.
계산만 한다 — 해석은 SKILL.md 지침과 reference/interpretation-guide.md 를 따른다.

사용(A=본인, B=상대 각각 --a-*/--b-* 로):
  python bin/gunghap.py \
     --a-year 1992 --a-month 8 --a-day 4 --a-hour 3 --a-minute 30 --a-gender female --a-name 나 \
     --b-year 1990 --b-month 2 --b-day 15 --b-hour 10 --b-gender male --b-name 상대 \
     [--timezone Asia/Seoul | --offset 540]
출력: 사람이 읽는 렌즈 요약(合/生/沖) + '===JSON===' 뒤 matchSheet 팩트(JSON).
"""
import argparse
import json
import os
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

from fate_py import bazi, match_sheet, format_match_sheet  # noqa: E402


def _chart(prefix, a, tz, offset):
    g = lambda k: getattr(a, f"{prefix}_{k}")
    inp = {"year": g("year"), "month": g("month"), "day": g("day")}
    if g("hour") is not None:
        inp["hour"] = g("hour")
        if g("minute") is not None:
            inp["minute"] = g("minute")
    if offset is not None:
        inp["utcOffsetMinutes"] = offset
    else:
        inp["timezone"] = tz
    try:
        return bazi(inp), None
    except Exception as e:
        if "timezone" in inp and tz == "Asia/Seoul":
            inp2 = {k: v for k, v in inp.items() if k != "timezone"}
            inp2["utcOffsetMinutes"] = 540
            return bazi(inp2), f"(참고: {prefix} tz 데이터 없어 오프셋 540분으로 계산)"
        raise e


def main():
    p = argparse.ArgumentParser(description="명경 궁합 계산")
    for who in ("a", "b"):
        p.add_argument(f"--{who}-year", type=int, required=True)
        p.add_argument(f"--{who}-month", type=int, required=True)
        p.add_argument(f"--{who}-day", type=int, required=True)
        p.add_argument(f"--{who}-hour", type=int, default=None)
        p.add_argument(f"--{who}-minute", type=int, default=None)
        p.add_argument(f"--{who}-gender", choices=["male", "female"], required=True)
        p.add_argument(f"--{who}-name", default=who.upper())
    p.add_argument("--timezone", default="Asia/Seoul")
    p.add_argument("--offset", type=int, default=None)
    a = p.parse_args()
    # argparse는 하이픈을 언더스코어로 → a_year 등.

    ca, na = _chart("a", a, a.timezone, a.offset)
    cb, nb = _chart("b", a, a.timezone, a.offset)

    A = {"bazi": ca, "gender": a.a_gender}
    B = {"bazi": cb, "gender": a.b_gender}
    sheet = match_sheet(A, B)

    print(f"■ 궁합 — {a.a_name}({'남' if a.a_gender=='male' else '여'}) ↔ {a.b_name}({'남' if a.b_gender=='male' else '여'})")
    for note in (na, nb):
        if note:
            print(note)
    print(f"  {a.a_name}: {ca['year']['stem']}{ca['year']['branch']} {ca['month']['stem']}{ca['month']['branch']} {ca['day']['stem']}{ca['day']['branch']}"
          + (f" {ca['hour']['stem']}{ca['hour']['branch']}" if ca.get('hour') else " (시간 모름)"))
    print(f"  {a.b_name}: {cb['year']['stem']}{cb['year']['branch']} {cb['month']['stem']}{cb['month']['branch']} {cb['day']['stem']}{cb['day']['branch']}"
          + (f" {cb['hour']['stem']}{cb['hour']['branch']}" if cb.get('hour') else " (시간 모름)"))
    print()
    print(format_match_sheet(sheet))

    print("\n===JSON===")
    print(json.dumps({
        "a": {"name": a.a_name, "gender": a.a_gender, "bazi": ca},
        "b": {"name": a.b_name, "gender": a.b_gender, "bazi": cb},
        "matchSheet": sheet,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
