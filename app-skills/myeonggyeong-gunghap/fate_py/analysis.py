"""1인 원국 2단계 — fate-js src/bazi/analysis.ts 1:1 미러링.

신강신약·격국·용신을 '사실'로 뽑는다 (analysisFacts).
"""

from .constants import (
    STEM_ELEMENTS,
    HIDDEN_STEMS,
    GENERATES,
    CONTROLS,
    CONTROLLED_BY,
    ELEMENTS,
)
from .rules import cells
from .judgments import ten_god
from .johu_table import JOHU_TABLE

# 십성 → 오행군(五行群) 분류.
GROUP_OF = {
    "비견": "비겁", "겁재": "비겁",
    "편인": "인성", "정인": "인성",
    "식신": "식상", "상관": "식상",
    "편재": "재성", "정재": "재성",
    "편관": "관성", "정관": "관성",
}


def _group_elements(dm: str) -> dict:
    """일간 오행 기준 각 오행군의 오행."""
    generator = dm
    for e in ELEMENTS:
        if GENERATES[e] == dm:
            generator = e
    return {
        "비겁": dm,
        "인성": generator,
        "식상": GENERATES[dm],
        "재성": CONTROLS[dm],
        "관성": CONTROLLED_BY[dm],
    }


_HIDDEN_ROLE = ["정기(正氣)", "중기(中氣)", "여기(餘氣)"]


def _role_at(count: int, idx: int) -> str:
    if count == 1:
        return "정기(正氣)"
    if count == 2:
        return "정기(正氣)" if idx == 0 else "여기(餘氣)"
    return _HIDDEN_ROLE[idx]


def _strength_facts(bazi: dict) -> dict:
    dm = bazi["day"]["stem"]
    dm_element = STEM_ELEMENTS[dm]
    cs = cells(bazi)

    # 득령 — 월지 본기 기준.
    month_main = HIDDEN_STEMS[bazi["month"]["branch"]][0]
    month_ten_god = ten_god(dm, month_main)
    deukryeong = {
        "present": GROUP_OF[month_ten_god] == "비겁" or GROUP_OF[month_ten_god] == "인성",
        "monthBranchTenGod": month_ten_god,
    }

    # 득지 — 일지 지장간에 비겁·인성.
    day_roots = []
    for hs in HIDDEN_STEMS[bazi["day"]["branch"]]:
        g = ten_god(dm, hs)
        if GROUP_OF[g] == "비겁" or GROUP_OF[g] == "인성":
            day_roots.append({"stem": hs, "tenGod": g})
    deukji = {"present": len(day_roots) > 0, "roots": day_roots}

    # 득세 — 세력 카운트(일간 자신 제외).
    def tally(with_hidden: bool) -> dict:
        by_group = {"비겁": 0, "인성": 0, "식상": 0, "재성": 0, "관성": 0}
        for c in cs:
            if c["name"] != "day":
                by_group[GROUP_OF[ten_god(dm, c["stem"])]] += 1
            if with_hidden:
                for hs in HIDDEN_STEMS[c["branch"]]:
                    by_group[GROUP_OF[ten_god(dm, hs)]] += 1
            else:
                by_group[GROUP_OF[ten_god(dm, HIDDEN_STEMS[c["branch"]][0])]] += 1
        return {
            "ally": by_group["비겁"] + by_group["인성"],
            "foe": by_group["식상"] + by_group["재성"] + by_group["관성"],
            "byGroup": by_group,
        }

    deukse = {"simple": tally(False), "withHidden": tally(True)}

    # 통근 — 일간과 같은 오행(비겁) 지장간이 있는 기둥.
    rooting = []
    for c in cs:
        via = []
        for hs in HIDDEN_STEMS[c["branch"]]:
            if STEM_ELEMENTS[hs] == dm_element:
                via.append({"stem": hs, "kind": "비겁"})
        if via:
            rooting.append({"pillar": c["name"], "via": via})

    # 투출 — 지장간이 천간에 드러남.
    stem_positions = {}
    for c in cs:
        stem_positions.setdefault(c["stem"], []).append(c["name"])
    revealed = []
    for c in cs:
        for hs in HIDDEN_STEMS[c["branch"]]:
            at = stem_positions.get(hs)
            if at is not None:
                revealed.append({"stem": hs, "fromBranch": c["name"], "atStems": at})

    # 참고 판정 — 다수설 휴리스틱.
    strong_count = len([
        x for x in (
            deukryeong["present"],
            deukji["present"],
            deukse["withHidden"]["ally"] >= deukse["withHidden"]["foe"],
        ) if x
    ])
    verdict = "신강" if strong_count >= 2 else ("신약" if strong_count == 0 else "중화")
    reference = {
        "verdict": verdict,
        "basis": "득령·득지·득세(지장간가중) 셋 중 성립 개수(2↑=신강, 0=신약, 1=중화). 다수설 개략 — 최종판정은 다운스트림 몫.",
    }

    return {
        "dayElement": dm_element,
        "deukryeong": deukryeong,
        "deukji": deukji,
        "deukse": deukse,
        "rooting": rooting,
        "revealed": revealed,
        "reference": reference,
    }


def _gyeok_name(g: str) -> str:
    m = {
        "정관": "정관격(正官格)", "편관": "편관격(偏官格·七殺)",
        "정재": "정재격(正財格)", "편재": "편재격(偏財格)",
        "정인": "정인격(正印格)", "편인": "편인격(偏印格)",
        "식신": "식신격(食神格)", "상관": "상관격(傷官格)",
        "비견": "건록격(建祿格)", "겁재": "양인격(羊刃格)",
    }
    return m[g]


def _gyeokguk_facts(bazi: dict) -> dict:
    dm = bazi["day"]["stem"]
    mb = bazi["month"]["branch"]
    hidden = HIDDEN_STEMS[mb]
    month_hidden_stems = [
        {"stem": hs, "tenGod": ten_god(dm, hs), "role": _role_at(len(hidden), i)}
        for i, hs in enumerate(hidden)
    ]

    stem_positions = {}
    for c in cells(bazi):
        stem_positions.setdefault(c["stem"], []).append(c["name"])

    revealed = []
    for h in month_hidden_stems:
        at = stem_positions.get(h["stem"], [])
        if len(at) > 0:
            revealed.append({**h, "atStems": at})

    candidates = []
    if revealed:
        for r in revealed:
            candidates.append({"name": _gyeok_name(r["tenGod"]), "tenGod": r["tenGod"], "basis": f"월지 {r['role']} 투출"})
    else:
        main = month_hidden_stems[0]
        candidates.append({"name": _gyeok_name(main["tenGod"]), "tenGod": main["tenGod"], "basis": "월령 본기(투출 없음)"})

    return {"monthBranch": mb, "monthHiddenStems": month_hidden_stems, "revealed": revealed, "candidates": candidates}


_SEASON_OF = {
    "寅": "봄(春)", "卯": "봄(春)", "辰": "봄(春)",
    "巳": "여름(夏)", "午": "여름(夏)", "未": "여름(夏)",
    "申": "가을(秋)", "酉": "가을(秋)", "戌": "가을(秋)",
    "亥": "겨울(冬)", "子": "겨울(冬)", "丑": "겨울(冬)",
}


def _yongsin_facts(bazi: dict, strength: dict) -> dict:
    dm = STEM_ELEMENTS[bazi["day"]["stem"]]
    ge = _group_elements(dm)

    strong = strength["reference"]["verdict"] == "신강"
    favorable = [ge["식상"], ge["재성"], ge["관성"]] if strong else [ge["인성"], ge["비겁"]]
    unfavorable = [ge["비겁"], ge["인성"]] if strong else [ge["식상"], ge["재성"], ge["관성"]]

    season = _SEASON_OF[bazi["month"]["branch"]]
    johu = JOHU_TABLE[bazi["day"]["stem"]][bazi["month"]["branch"]]

    johu_out = {
        "season": season,
        "main": list(johu["main"]),
        "sub": list(johu["sub"]),
    }
    if johu.get("cond"):
        johu_out["cond"] = johu["cond"]
    johu_out["basis"] = "궁통보감 조후표(月支×日干) — 표 사실만, 취사는 다운스트림 몫."

    return {
        "eokbu": {
            "method": "억부(抑扶)",
            "favorable": favorable,
            "unfavorable": unfavorable,
            "basis": (
                f"참고판정 {strength['reference']['verdict']} → "
                f"{'설기·극(식상·재·관)' if strong else '생조(인성·비겁)'} 희신. 최종 용신은 다운스트림 몫."
            ),
        },
        "johu": johu_out,
    }


def analysis_facts(bazi: dict) -> dict:
    strength = _strength_facts(bazi)
    return {
        "strength": strength,
        "gyeokguk": _gyeokguk_facts(bazi),
        "yongsin": _yongsin_facts(bazi, strength),
    }
