"""궁합 판단(判斷) 추출 — fate-js src/match/judgments.ts 1:1 미러링.

tenGod·tenGodDistribution·nayinOf·judgeMatch 및 십성·납음·신살 헬퍼.
"""

import math
import re

from .constants import (
    STEM_ELEMENTS,
    STEM_YINYANG,
    STEM_INDEX,
    BRANCH_INDEX,
    BRANCH_ELEMENTS,
    GENERATES,
    CONTROLS,
    HIDDEN_STEMS,
    ELEMENTS,
)
from .rules import cells
from .crosses import cross_judgments
from .judgments_constants import (
    NAYIN_PAIRS,
    SINSAL_FROM_SAMHAP,
    HONGYEOM_BY_STEM,
    CHEONEUL_BY_STEM,
    MUNCHANG_BY_STEM,
    YANGIN_BY_STEM,
    BAEKHO_PILLARS,
    GWAEGANG_PILLARS,
    GWIMUN_PAIRS,
)

# 십성 10종 고정 순서 — 분포 벡터의 컬럼 순서.
TEN_GODS = ("비견", "겁재", "식신", "상관", "편재", "정재", "편관", "정관", "편인", "정인")

ELEMENT_KO = {
    "wood": "목(木)",
    "fire": "화(火)",
    "earth": "토(土)",
    "metal": "금(金)",
    "water": "수(水)",
}

PILLAR_KO = {"year": "년", "month": "월", "day": "일", "hour": "시"}

_PAREN_RE = re.compile(r"\(([^)]+)\)")


def ten_god(day_master: str, other: str) -> str:
    """일간(day) 대비 어떤 천간 other 의 십성을 판정한다."""
    dm = STEM_ELEMENTS[day_master]
    oe = STEM_ELEMENTS[other]
    same = STEM_YINYANG[day_master] == STEM_YINYANG[other]

    if dm == oe:
        return "비견" if same else "겁재"
    if GENERATES[dm] == oe:
        return "식신" if same else "상관"
    if CONTROLS[dm] == oe:
        return "편재" if same else "정재"
    if CONTROLS[oe] == dm:
        return "편관" if same else "정관"
    # 남은 경우: oe 가 dm 을 생함.
    return "편인" if same else "정인"


TEN_GOD_HANJA = {
    "비견": "比肩",
    "겁재": "劫財",
    "식신": "食神",
    "상관": "傷官",
    "편재": "偏財",
    "정재": "正財",
    "편관": "偏官",
    "정관": "正官",
    "편인": "偏印",
    "정인": "正印",
}


def _empty_ten_god_count() -> dict:
    return {g: 0 for g in TEN_GODS}


def ten_god_distribution(bazi: dict) -> dict:
    """한 사주의 천간 4자(시 미상이면 3자)를 일간 기준 십성 분포로 집계."""
    dm = bazi["day"]["stem"]
    out = _empty_ten_god_count()
    for cell in cells(bazi):
        if cell["name"] == "day":
            continue
        out[ten_god(dm, cell["stem"])] += 1
    return out


def _cross_ten_god(id_, viewer_label, target_label, viewer, target) -> dict:
    dm = viewer["day"]["stem"]
    other = target["day"]["stem"]
    g = ten_god(dm, other)
    return {
        "id": id_,
        "label": f"{viewer_label} 기준 {target_label} 일간 십성",
        "category": g,
        "present": True,
        "statement": (
            f"{viewer_label} 일간 {dm}({ELEMENT_KO[STEM_ELEMENTS[dm]]})에게 "
            f"{target_label} 일간 {other}({ELEMENT_KO[STEM_ELEMENTS[other]]})은(는) "
            f"{g}({TEN_GOD_HANJA[g]})에 해당한다."
        ),
        "source": "자평진전·연해자평(십성)",
        "detail": {"dayMaster": dm, "other": other, "tenGod": g},
    }


def _is_wealth(g: str) -> bool:
    return g == "정재" or g == "편재"


def _is_officer(g: str) -> bool:
    return g == "정관" or g == "편관"


def _spouse_star(id_, subject_label, partner_label, subject, partner) -> dict:
    gender = subject.get("gender")
    dm = subject["bazi"]["day"]["stem"]
    want_wealth = gender == "male"
    want_officer = gender == "female"

    if not gender:
        return {
            "id": id_,
            "label": f"{subject_label}의 배우자성 공급",
            "category": False,
            "present": False,
            "statement": f"{subject_label}의 성별 미제공 — 배우자성 판정 보류.",
            "source": "자평진전(배우자성)",
            "basis": "남명=재성(처), 여명=관성(부)",
        }

    def wants_star(g):
        return (want_wealth and _is_wealth(g)) or (want_officer and _is_officer(g))

    partner_cells = cells(partner)
    supply_pillars = []
    revealed_pillars = []
    hidden_pillars = []
    jeong = 0
    pyeon = 0

    def count_star(g):
        nonlocal jeong, pyeon
        if not wants_star(g):
            return
        if g == "정재" or g == "정관":
            jeong += 1
        else:
            pyeon += 1

    target_ko = "재성(財)" if want_wealth else "관성(官)"
    for c in partner_cells:
        in_stem = wants_star(ten_god(dm, c["stem"]))
        in_hidden = any(wants_star(ten_god(dm, hs)) for hs in HIDDEN_STEMS[c["branch"]])
        if in_stem or in_hidden:
            supply_pillars.append(c["name"])
        if in_stem:
            revealed_pillars.append(c["name"])
        elif in_hidden:
            hidden_pillars.append(c["name"])
        count_star(ten_god(dm, c["stem"]))
        for hs in HIDDEN_STEMS[c["branch"]]:
            count_star(ten_god(dm, hs))

    day_branch = partner["day"]["branch"]
    main_stem = next(
        (hs for hs in HIDDEN_STEMS[day_branch] if STEM_ELEMENTS[hs] == BRANCH_ELEMENTS[day_branch]),
        None,
    )
    if main_stem and wants_star(ten_god(dm, main_stem)):
        day_seat = "본기"
    elif any(wants_star(ten_god(dm, hs)) for hs in HIDDEN_STEMS[day_branch]):
        day_seat = "장간"
    else:
        day_seat = False
    present = len(supply_pillars) > 0
    spouse_word = "처(妻)" if gender == "male" else "부(夫)"
    return {
        "id": id_,
        "label": f"{subject_label}의 배우자성 공급",
        "category": present,
        "present": present,
        "statement": (
            f"{partner_label}이(가) {subject_label}의 배우자성 {target_ko}={spouse_word}을(를) "
            f"{'·'.join(PILLAR_KO[p] for p in supply_pillars)}주 천간·지장간으로 공급한다."
            if present else
            f"{partner_label}은(는) {subject_label}의 배우자성 {target_ko}을(를) 천간·지장간으로 공급하지 않는다."
        ),
        "source": "자평진전(배우자성)",
        "basis": "남명=재성(처), 여명=관성(부) — 천간·지장간 포함",
        "detail": {
            "gender": gender,
            "spouseStar": target_ko,
            "supplyPillars": supply_pillars,
            "revealedPillars": revealed_pillars,
            "hiddenPillars": hidden_pillars,
            "daySeat": day_seat,
            "jeong": jeong,
            "pyeon": pyeon,
        },
    }


def nayin_of(stem: str, branch: str):
    """간지 두 글자(예: 甲子)의 납음을 구한다. 불가능한 조합이면 None."""
    si = STEM_INDEX[stem]
    bi = BRANCH_INDEX[branch]
    for k in range(60):
        if k % 10 == si and k % 12 == bi:
            pair = NAYIN_PAIRS[math.floor(k / 2)]
            return {"name": pair["name"], "element": pair["element"]}
    return None


def _nayin_cells(bazi: dict) -> list:
    out = []
    for c in cells(bazi):
        ny = nayin_of(c["stem"], c["branch"])
        if not ny:
            continue
        out.append({
            "pillar": c["name"],
            "ganzhi": c["stem"] + c["branch"],
            "name": ny["name"],
            "element": ny["element"],
        })
    return out


def _nayin_outer_reading(subject: dict, candidate: dict) -> dict:
    s = nayin_of(subject["year"]["stem"], subject["year"]["branch"])
    c = nayin_of(candidate["year"]["stem"], candidate["year"]["branch"])
    if not s or not c:
        return {
            "id": "nayin_outer",
            "label": "납음 겉궁합",
            "category": False,
            "present": False,
            "statement": "년주 간지 납음을 확정할 수 없어 겉궁합 판정 보류.",
            "source": "삼명통회·전통 궁합(납음)",
            "basis": "년주 납음 기준(전통 겉궁합)",
        }
    if s["element"] == c["element"]:
        category = "same"
        rel_ko = "비화(比和)"
    elif GENERATES[s["element"]] == c["element"] or GENERATES[c["element"]] == s["element"]:
        category = "generates"
        rel_ko = "상생(相生)"
    else:
        category = "controls"
        rel_ko = "상극(相剋)"
    return {
        "id": "nayin_outer",
        "label": "납음 겉궁합",
        "category": category,
        "present": True,
        "statement": (
            f"주체 년주 {subject['year']['stem']}{subject['year']['branch']}={s['name']}({ELEMENT_KO[s['element']]}), "
            f"후보 년주 {candidate['year']['stem']}{candidate['year']['branch']}={c['name']}({ELEMENT_KO[c['element']]}) — "
            f"두 납음오행은 {rel_ko} 관계다."
        ),
        "source": "삼명통회·전통 궁합(납음)",
        "basis": "년주 납음 기준(전통 겉궁합)",
        "detail": {
            "subjectNayin": s["name"],
            "subjectElement": s["element"],
            "candidateNayin": c["name"],
            "candidateElement": c["element"],
        },
    }


def _samhap_sinsal(id_, label, key, ref_branch, target_bazi) -> dict:
    hit = SINSAL_FROM_SAMHAP[ref_branch][key]
    pillars = []
    for c in cells(target_bazi):
        if c["branch"] == hit:
            pillars.append(c["name"])
    present = len(pillars) > 0
    return {
        "id": id_,
        "label": label,
        "category": present,
        "present": present,
        "statement": (
            f"기준 일지 {ref_branch}의 {label} 지지는 {hit} — 상대 사주 "
            f"{'·'.join(PILLAR_KO[p] for p in pillars)}주에 있어 성립한다."
            if present else
            f"기준 일지 {ref_branch}의 {label} 지지 {hit} 없음."
        ),
        "source": "삼명통회·연해자평(신살)",
        "basis": "일지(삼합) 기준 — 년지 기준 변형 있음",
        "detail": {"refBranch": ref_branch, "target": hit, "pillars": pillars},
    }


def _stem_branch_sinsal(id_, label, ref_stem, table, source, target_bazi) -> dict:
    hit = table[ref_stem]
    pillars = []
    for c in cells(target_bazi):
        if c["branch"] == hit:
            pillars.append(c["name"])
    present = len(pillars) > 0
    return {
        "id": id_,
        "label": label,
        "category": present,
        "present": present,
        "statement": (
            f"기준 일간 {ref_stem}의 {label} 지지 {hit} — 상대 사주 "
            f"{'·'.join(PILLAR_KO[p] for p in pillars)}주에 있어 성립한다."
            if present else
            f"기준 일간 {ref_stem}의 {label} 지지 {hit} 없음."
        ),
        "source": source,
        "basis": "일간 기준",
        "detail": {"refStem": ref_stem, "target": hit, "pillars": pillars},
    }


def _yangin_sinsal(ref_stem, target_bazi) -> dict:
    source = "자평진전(양인)"
    if STEM_YINYANG[ref_stem] != "yang":
        return {
            "id": "yangin",
            "label": "양인살(羊刃)",
            "category": False,
            "present": False,
            "statement": f"기준 일간 {ref_stem}은(는) 음간 — 양인살 미인정(양간만, 다수설).",
            "source": source,
            "basis": "일간 기준(양간 정설 — 음간 미포함)",
            "detail": {"refStem": ref_stem, "pillars": []},
        }
    hit = YANGIN_BY_STEM[ref_stem]
    pillars = []
    for c in cells(target_bazi):
        if c["branch"] == hit:
            pillars.append(c["name"])
    present = len(pillars) > 0
    return {
        "id": "yangin",
        "label": "양인살(羊刃)",
        "category": present,
        "present": present,
        "statement": (
            f"기준 일간 {ref_stem}의 양인살(羊刃) 지지 {hit} — 상대 사주 "
            f"{'·'.join(PILLAR_KO[p] for p in pillars)}주에 있어 성립한다."
            if present else
            f"기준 일간 {ref_stem}의 양인살(羊刃) 지지 {hit} 없음."
        ),
        "source": source,
        "basis": "일간 기준(양간 정설 — 음간 미포함)",
        "detail": {"refStem": ref_stem, "target": hit, "pillars": pillars},
    }


def _cheoneul_sinsal(ref_stem, target_bazi) -> dict:
    targets = CHEONEUL_BY_STEM[ref_stem]
    pillars = []
    for c in cells(target_bazi):
        if c["branch"] in targets:
            pillars.append(c["name"])
    present = len(pillars) > 0
    return {
        "id": "cheoneul",
        "label": "천을귀인(天乙貴人)",
        "category": present,
        "present": present,
        "statement": (
            f"기준 일간 {ref_stem}의 천을귀인 지지 {'·'.join(targets)} — 상대 사주 "
            f"{'·'.join(PILLAR_KO[p] for p in pillars)}주에 있어 성립한다(최고 길신)."
            if present else
            f"기준 일간 {ref_stem}의 천을귀인 지지 {'·'.join(targets)} 없음."
        ),
        "source": "삼명통회(천을귀인)",
        "basis": "일간 기준",
        "detail": {"refStem": ref_stem, "targets": list(targets), "pillars": pillars},
    }


def _pillar_sinsal(id_, label, pillar_set, source, target_bazi) -> dict:
    pillars = []
    for c in cells(target_bazi):
        if (c["stem"] + c["branch"]) in pillar_set:
            pillars.append(c["name"])
    present = len(pillars) > 0
    return {
        "id": id_,
        "label": label,
        "category": present,
        "present": present,
        "statement": (
            f"상대 사주 {'·'.join(PILLAR_KO[p] for p in pillars)}주가 {label} 간지에 해당한다."
            if present else
            f"{label} 간지 없음."
        ),
        "source": source,
        "basis": "간지(주) 자체 판정 — 상대 사주 기준",
        "detail": {"pillars": pillars},
    }


def _gwimun_sinsal(ref_branch, target_bazi) -> dict:
    pillars = []
    for c in cells(target_bazi):
        if c["branch"] == ref_branch:
            continue
        paired = any((ref_branch in s and c["branch"] in s) for s in GWIMUN_PAIRS)
        if paired:
            pillars.append(c["name"])
    present = len(pillars) > 0
    return {
        "id": "gwimun",
        "label": "귀문관살(鬼門關殺)",
        "category": present,
        "present": present,
        "statement": (
            f"기준 일지 {ref_branch}와 상대 {'·'.join(PILLAR_KO[p] for p in pillars)}주 지지가 "
            f"귀문관살 쌍을 이룬다(신경과민·집착)."
            if present else
            f"기준 일지 {ref_branch} 기준 귀문관살 없음."
        ),
        "source": "궁합 통설(귀문관살)",
        "basis": "일지 기준 쌍 판정",
        "detail": {"refBranch": ref_branch, "pillars": pillars},
    }


def _sinsal_for(ref_bazi, target_bazi) -> list:
    ref_branch = ref_bazi["day"]["branch"]
    ref_stem = ref_bazi["day"]["stem"]
    return [
        _samhap_sinsal("dohwa", "도화살(桃花)", "dohwa", ref_branch, target_bazi),
        _samhap_sinsal("yeokma", "역마살(驛馬)", "yeokma", ref_branch, target_bazi),
        _samhap_sinsal("hwagae", "화개살(華蓋)", "hwagae", ref_branch, target_bazi),
        _stem_branch_sinsal("hongyeom", "홍염살(紅艶)", ref_stem, HONGYEOM_BY_STEM, "명리 통설(홍염)", target_bazi),
        _cheoneul_sinsal(ref_stem, target_bazi),
        _stem_branch_sinsal("munchang", "문창귀인(文昌貴人)", ref_stem, MUNCHANG_BY_STEM, "삼명통회(문창귀인)", target_bazi),
        _yangin_sinsal(ref_stem, target_bazi),
        _pillar_sinsal("baekho", "백호살(白虎)", BAEKHO_PILLARS, "명리 통설(백호대살)", target_bazi),
        _pillar_sinsal("gwaegang", "괴강살(魁罡)", GWAEGANG_PILLARS, "명리 통설(괴강)", target_bazi),
        _gwimun_sinsal(ref_branch, target_bazi),
    ]


def judge_match(subject: dict, candidate: dict, facts: list) -> dict:
    """두 사주의 판단 파생값(yongsinSupply 제외)을 뽑는다."""
    sb = subject["bazi"]
    cb = candidate["bazi"]

    palace = _build_palace_summary(facts)

    return {
        "tenGod": {
            "subjectDistribution": ten_god_distribution(sb),
            "candidateDistribution": ten_god_distribution(cb),
            "candidateToSubject": _cross_ten_god("tengod_candidate_to_subject", "주체", "후보", sb, cb),
            "subjectToCandidate": _cross_ten_god("tengod_subject_to_candidate", "후보", "주체", cb, sb),
            "spouseStarForSubject": _spouse_star("spouse_star_subject", "주체", "후보", subject, cb),
            "spouseStarForCandidate": _spouse_star("spouse_star_candidate", "후보", "주체", candidate, sb),
        },
        "nayin": {
            "subjectCells": _nayin_cells(sb),
            "candidateCells": _nayin_cells(cb),
            "outerReading": _nayin_outer_reading(sb, cb),
        },
        "sinsal": {
            "candidateForSubject": _sinsal_for(sb, cb),
            "subjectForCandidate": _sinsal_for(cb, sb),
        },
        "palace": palace,
        "hapChungOverlap": _build_hap_chung_overlap(facts),
        "jaenghap": _build_jaenghap(facts),
        "chungWangswe": _build_chung_wangswe(subject, candidate, facts),
        "cross": cross_judgments(sb, cb),
    }


# ── 충 왕쇠(旺者沖衰) ────────────────────────────────────────────────

WANGSWE_ORDER = ("死", "囚", "休", "相", "旺")


def _wangswe_grade(el, season_el) -> str:
    if el == season_el:
        return "旺"
    if GENERATES[season_el] == el:
        return "相"
    if GENERATES[el] == season_el:
        return "休"
    if CONTROLS[el] == season_el:
        return "囚"
    return "死"


def _build_chung_wangswe(subject, candidate, facts) -> dict:
    clash = next((f for f in facts if f["id"] == "branch_clash"), None)
    season_a = BRANCH_ELEMENTS[subject["bazi"]["month"]["branch"]]
    season_b = BRANCH_ELEMENTS[candidate["bazi"]["month"]["branch"]]
    pillar_hanja = {"year": "年", "month": "月", "day": "日", "hour": "時"}
    edges = clash["edges"] if clash else []
    entries = []
    for e in edges:
        g_a = _wangswe_grade(BRANCH_ELEMENTS[e["subject"]["glyph"]], season_a)
        g_b = _wangswe_grade(BRANCH_ELEMENTS[e["object"]["glyph"]], season_b)
        ra = WANGSWE_ORDER.index(g_a)
        rb = WANGSWE_ORDER.index(g_b)
        verdict = "相持" if ra == rb else ("A拔" if ra < rb else "B拔")
        entries.append(
            f"A{pillar_hanja[e['subject']['pillar']]}{e['subject']['glyph']}({g_a})-"
            f"B{pillar_hanja[e['object']['pillar']]}{e['object']['glyph']}({g_b})→{verdict}"
        )
    present = len(entries) > 0
    return {
        "id": "chung_wangswe",
        "label": "충 왕쇠(旺者沖衰)",
        "category": present,
        "present": present,
        "statement": (
            f"六沖 {len(entries)}처의 왕쇠(월령 왕상휴수 기준): {', '.join(entries)}."
            if present else "六沖 없음 — 왕쇠 판정 대상 없음."
        ),
        "source": "적천수(旺者沖衰衰者拔) — 왕쇠=월령 왕상휴수 고전표; 쌍반 충 적용은 대운·세운 충 유추(원전 직접 아님)",
        "detail": {"entries": entries},
    }


def _label_paren(label: str) -> str:
    m = _PAREN_RE.search(label)
    return m.group(1) if m else label


def _build_jaenghap(facts) -> dict:
    KINDS = {"stem_hap", "branch_yukhap"}
    seen = {}
    for f in facts:
        if not f["present"] or f["id"] not in KINDS:
            continue
        name = _label_paren(f["label"])
        for e in f["edges"]:
            for who, end in (("A", e["subject"]), ("B", e["object"])):
                key = f"{who}:{end['pillar']}:{end['glyph']}:{name}"
                cur = seen.get(key)
                if cur is None:
                    cur = {"who": who, "pillar": end["pillar"], "glyph": end["glyph"], "label": name, "n": 0}
                cur["n"] += 1
                seen[key] = cur
    contested = [c for c in seen.values() if c["n"] >= 2]
    present = len(contested) > 0
    pillar_hanja = {"year": "年", "month": "月", "day": "日", "hour": "時"}

    def describe(c):
        return f"{c['who']}{pillar_hanja[c['pillar']]}{c['glyph']}({c['label']}×{c['n']})"

    return {
        "id": "jaenghap",
        "label": "쟁합·투합",
        "category": present,
        "present": present,
        "statement": (
            f"같은 글자가 같은 종류 합을 여럿 맺음: {', '.join(describe(c) for c in contested)}."
            if present else "쟁합·투합 없음."
        ),
        "source": "자평진전(爭合·妒合)",
        "detail": {"cells": [describe(c) for c in contested]},
    }


def _build_hap_chung_overlap(facts) -> dict:
    HAP = {"branch_yukhap", "branch_samhap", "branch_banghap"}
    CHUNG = {"branch_clash", "branch_hyung", "branch_hae", "branch_pa", "branch_wonjin"}
    seen = {}

    def touch(who, pillar, glyph, kind, label):
        key = f"{who}:{pillar}:{glyph}"
        cur = seen.get(key)
        if cur is None:
            cur = {"who": who, "pillar": pillar, "glyph": glyph, "hap": set(), "chung": set(), "_hap_o": [], "_chung_o": []}
        # Set 삽입 순서 보존을 위해 리스트 동반(중복 방지).
        if label not in cur[kind]:
            cur[kind].add(label)
            cur["_hap_o" if kind == "hap" else "_chung_o"].append(label)
        seen[key] = cur

    for f in facts:
        if not f["present"]:
            continue
        if f["id"] in HAP:
            kind = "hap"
        elif f["id"] in CHUNG:
            kind = "chung"
        else:
            continue
        name = _label_paren(f["label"])
        for e in f["edges"]:
            touch("A", e["subject"]["pillar"], e["subject"]["glyph"], kind, name)
            touch("B", e["object"]["pillar"], e["object"]["glyph"], kind, name)

    overlaps = [c for c in seen.values() if len(c["hap"]) > 0 and len(c["chung"]) > 0]
    present = len(overlaps) > 0
    pillar_hanja = {"year": "年", "month": "月", "day": "日", "hour": "時"}

    def describe(c):
        return (
            f"{c['who']}{pillar_hanja[c['pillar']]}{c['glyph']}"
            f"({'·'.join(c['_hap_o'])}+{'·'.join(c['_chung_o'])})"
        )

    return {
        "id": "hap_chung_overlap",
        "label": "합충 병존",
        "category": present,
        "present": present,
        "statement": (
            f"같은 글자가 합과 충에 동시 성립: {', '.join(describe(c) for c in overlaps)}."
            if present else "지지 합과 충이 같은 글자에서 겹치지 않음."
        ),
        "source": "합충 병존",
        "detail": {"cells": [describe(c) for c in overlaps]},
    }


def _build_palace_summary(facts) -> dict:
    outer_harmony = 0
    outer_clash = 0
    inner_harmony = 0
    inner_clash = 0

    for f in facts:
        for e in f["edges"]:
            both_year = e["subject"]["pillar"] == "year" and e["object"]["pillar"] == "year"
            both_day = e["subject"]["pillar"] == "day" and e["object"]["pillar"] == "day"
            if both_year:
                if f["polarity"] == "harmony":
                    outer_harmony += 1
                elif f["polarity"] == "clash":
                    outer_clash += 1
            if both_day:
                if f["polarity"] == "harmony":
                    inner_harmony += 1
                elif f["polarity"] == "clash":
                    inner_clash += 1

    return {
        "id": "palace_summary",
        "label": "겉궁합·속궁합 분류",
        "category": True,
        "present": True,
        "statement": (
            f"겉궁합(연주): 화합 {outer_harmony} · 충돌 {outer_clash}건. "
            f"속궁합(일지): 화합 {inner_harmony} · 충돌 {inner_clash}건."
        ),
        "source": "12관계 위치 집계",
        "basis": "연주=겉(사회적), 일지=속(배우자궁)",
        "detail": {
            "outerHarmony": outer_harmony,
            "outerClash": outer_clash,
            "innerHarmony": inner_harmony,
            "innerClash": inner_clash,
        },
    }
