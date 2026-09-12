"""1인 원국 FactSheet — fate-js src/bazi/analyze.ts 1:1 미러링.

analyze(subject) → BaziAnalysis.
"""

from .constants import (
    STEM_ELEMENTS,
    BRANCH_ELEMENTS,
    STEM_YINYANG,
    STEM_INDEX,
    BRANCH_INDEX,
    BRANCHES,
    HIDDEN_STEMS,
    STEM_COMBINATIONS,
    BRANCH_LIUHE,
    BRANCH_CLASH,
    BRANCH_HARM,
)
from .match_constants import (
    STEM_CLASH,
    BRANCH_PA,
    BRANCH_WONJIN,
    BRANCH_SAMHAP,
    BRANCH_BANGHAP,
    BRANCH_HYUNG,
)
from .judgments_constants import (
    CHEONEUL_BY_STEM,
    MUNCHANG_BY_STEM,
    HONGYEOM_BY_STEM,
    YANGIN_BY_STEM,
    BAEKHO_PILLARS,
    GWAEGANG_PILLARS,
    GWIMUN_PAIRS,
)
from .rules import cells
from .judgments import ten_god, ten_god_distribution, nayin_of
from .bazi_constants import twelve_stage, twelve_sinsal
from .analysis import analysis_facts

BAZIANALYSIS_SCHEMA_VERSION = "bazi-analysis"


def _branch_yinyang(b: str) -> str:
    return "yang" if BRANCH_INDEX[b] % 2 == 0 else "yin"


def _empty_element_count() -> dict:
    return {"wood": 0, "fire": 0, "earth": 0, "metal": 0, "water": 0}


def _hidden_role(count: int, idx: int) -> str:
    if count == 1:
        return "정기(正氣)"
    if count == 2:
        return "정기(正氣)" if idx == 0 else "여기(餘氣)"
    return ["정기(正氣)", "중기(中氣)", "여기(餘氣)"][idx]


def _void_branches_of(bazi: dict) -> list:
    si = STEM_INDEX[bazi["day"]["stem"]]
    bi = BRANCH_INDEX[bazi["day"]["branch"]]
    base = (bi - si + 12) % 12
    return [BRANCHES[(base + 10) % 12], BRANCHES[(base + 11) % 12]]


def _stem_sinsal(id_, label, targets, bazi, basis) -> dict:
    pillars = []
    for c in cells(bazi):
        if c["branch"] in targets:
            pillars.append(c["name"])
    return {"id": id_, "label": label, "present": len(pillars) > 0, "pillars": pillars, "basis": basis}


def _pillar_sinsal(id_, label, s, bazi) -> dict:
    pillars = []
    for c in cells(bazi):
        if (c["stem"] + c["branch"]) in s:
            pillars.append(c["name"])
    return {"id": id_, "label": label, "present": len(pillars) > 0, "pillars": pillars, "basis": "간지(주) 자체"}


def _gwimun_sinsal(bazi: dict) -> dict:
    cs = cells(bazi)
    pillars = {}
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            paired = any((cs[i]["branch"] in s and cs[j]["branch"] in s) for s in GWIMUN_PAIRS)
            if paired:
                pillars[cs[i]["name"]] = True
                pillars[cs[j]["name"]] = True
    return {
        "id": "gwimun",
        "label": "귀문관살(鬼門關殺)",
        "present": len(pillars) > 0,
        "pillars": list(pillars.keys()),
        "basis": "원국 내 지지 쌍",
    }


def _bazi_sinsal(bazi: dict) -> list:
    dm = bazi["day"]["stem"]
    yangin_targets = [YANGIN_BY_STEM[dm]] if STEM_YINYANG[dm] == "yang" else []
    return [
        _stem_sinsal("cheoneul", "천을귀인(天乙貴人)", CHEONEUL_BY_STEM[dm], bazi, "일간 기준"),
        _stem_sinsal("munchang", "문창귀인(文昌貴人)", [MUNCHANG_BY_STEM[dm]], bazi, "일간 기준"),
        _stem_sinsal("hongyeom", "홍염살(紅艶殺)", [HONGYEOM_BY_STEM[dm]], bazi, "일간 기준"),
        _stem_sinsal("yangin", "양인살(羊刃)", yangin_targets, bazi, "일간 기준(양간 정설 — 음간 미포함)"),
        _pillar_sinsal("baekho", "백호살(白虎大殺)", BAEKHO_PILLARS, bazi),
        _pillar_sinsal("gwaegang", "괴강살(魁罡)", GWAEGANG_PILLARS, bazi),
        _gwimun_sinsal(bazi),
    ]


def _paired_in_sets(sets, x, y) -> bool:
    if x == y:
        return False
    return any((x in s and y in s) for s in sets)


def _build_hyung_pairs():
    m = {}
    for rule in BRANCH_HYUNG:
        b = rule["branches"]
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                m["".join(sorted([b[i], b[j]]))] = rule["name"]
        if rule["kind"] == "jahyung" and len(b) > 0 and b[0]:
            m[b[0] + b[0]] = rule["name"]
    return m


_HYUNG_PAIRS = _build_hyung_pairs()


def _internal_relations(bazi: dict) -> list:
    cs = cells(bazi)
    out = []

    pair_specs = [
        {"id": "stem_hap", "label": "천간합(天干合)", "polarity": "harmony", "accessor": "stem", "sets": STEM_COMBINATIONS},
        {"id": "stem_clash", "label": "천간충(天干沖)", "polarity": "clash", "accessor": "stem", "sets": STEM_CLASH},
        {"id": "branch_yukhap", "label": "지지 육합(六合)", "polarity": "harmony", "accessor": "branch", "sets": BRANCH_LIUHE},
        {"id": "branch_clash", "label": "지지충(六沖)", "polarity": "clash", "accessor": "branch", "sets": BRANCH_CLASH},
        {"id": "branch_hae", "label": "지지해(六害)", "polarity": "clash", "accessor": "branch", "sets": BRANCH_HARM},
        {"id": "branch_pa", "label": "지지파(六破)", "polarity": "clash", "accessor": "branch", "sets": BRANCH_PA},
        {"id": "branch_wonjin", "label": "원진(怨嗔)", "polarity": "clash", "accessor": "branch", "sets": BRANCH_WONJIN},
    ]

    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            a = cs[i]
            b = cs[j]
            for spec in pair_specs:
                ga = a["stem"] if spec["accessor"] == "stem" else a["branch"]
                gb = b["stem"] if spec["accessor"] == "stem" else b["branch"]
                if _paired_in_sets(spec["sets"], ga, gb):
                    out.append({
                        "id": spec["id"], "label": spec["label"], "polarity": spec["polarity"],
                        "pillars": [a["name"], b["name"]], "glyphs": [ga, gb],
                    })
            hy = _HYUNG_PAIRS.get("".join(sorted([a["branch"], b["branch"]])))
            if hy:
                out.append({
                    "id": "branch_hyung", "label": f"형(刑)·{hy}", "polarity": "clash",
                    "pillars": [a["name"], b["name"]], "glyphs": [a["branch"], b["branch"]],
                })

    for groups, id_, label in (
        (BRANCH_SAMHAP, "branch_samhap", "삼합(三合)"),
        (BRANCH_BANGHAP, "branch_banghap", "방합(方合)"),
    ):
        for g in groups:
            member_cells = [c for c in cs if c["branch"] in g["branches"]]
            # Set 삽입 순서 보존.
            distinct = {}
            for c in member_cells:
                distinct[c["branch"]] = True
            if len(distinct) < 2 or g["king"] not in distinct:
                continue
            out.append({
                "id": id_ if len(distinct) >= 3 else f"{id_}_ban",
                "label": label if len(distinct) >= 3 else f"{label} 반합(半合)",
                "polarity": "harmony",
                "pillars": [c["name"] for c in member_cells],
                "glyphs": list(distinct.keys()),
                "element": g["element"],
            })

    return out


def _element_distribution(bazi: dict) -> dict:
    simple = _empty_element_count()
    with_hidden = _empty_element_count()
    for c in cells(bazi):
        simple[STEM_ELEMENTS[c["stem"]]] += 1
        simple[BRANCH_ELEMENTS[c["branch"]]] += 1
        with_hidden[STEM_ELEMENTS[c["stem"]]] += 1
        for hs in HIDDEN_STEMS[c["branch"]]:
            with_hidden[STEM_ELEMENTS[hs]] += 1
    return {"simple": simple, "withHidden": with_hidden}


def analyze(subject: dict) -> dict:
    bazi = subject["bazi"]
    dm = bazi["day"]["stem"]
    year_branch = bazi["year"]["branch"]
    day_branch = bazi["day"]["branch"]
    voids = _void_branches_of(bazi)

    pillars = []
    for c in cells(bazi):
        is_day_stem = c["name"] == "day"
        hidden = []
        for idx, hs in enumerate(HIDDEN_STEMS[c["branch"]]):
            hidden.append({
                "glyph": hs,
                "element": STEM_ELEMENTS[hs],
                "yinyang": STEM_YINYANG[hs],
                "tenGod": ten_god(dm, hs),
                "role": _hidden_role(len(HIDDEN_STEMS[c["branch"]]), idx),
            })
        branch_main = HIDDEN_STEMS[c["branch"]][0]
        pillars.append({
            "name": c["name"],
            "stem": {
                "glyph": c["stem"],
                "element": STEM_ELEMENTS[c["stem"]],
                "yinyang": STEM_YINYANG[c["stem"]],
                "tenGod": None if is_day_stem else ten_god(dm, c["stem"]),
            },
            "branch": {
                "glyph": c["branch"],
                "element": BRANCH_ELEMENTS[c["branch"]],
                "yinyang": _branch_yinyang(c["branch"]),
                "tenGod": ten_god(dm, branch_main),
                "hiddenStems": hidden,
                "twelveStage": twelve_stage(dm, c["branch"]),
                "sinsalFromYear": twelve_sinsal(year_branch, c["branch"]),
                "sinsalFromDay": twelve_sinsal(day_branch, c["branch"]),
                "isVoid": c["branch"] in voids,
            },
            "ganzhi": c["stem"] + c["branch"],
            "nayin": nayin_of(c["stem"], c["branch"]),
        })

    out = {
        "schemaVersion": BAZIANALYSIS_SCHEMA_VERSION,
        "bazi": bazi,
    }
    if subject.get("gender"):
        out["gender"] = subject["gender"]
    out["dayMaster"] = {
        "glyph": dm,
        "element": STEM_ELEMENTS[dm],
        "yinyang": STEM_YINYANG[dm],
    }
    out["pillars"] = pillars
    out["voidBranches"] = voids
    out["tenGodDistribution"] = ten_god_distribution(bazi)
    out["elementDistribution"] = _element_distribution(bazi)
    out["sinsal"] = _bazi_sinsal(bazi)
    out["internalRelations"] = _internal_relations(bazi)
    out["analysis"] = analysis_facts(bazi)
    out["policy"] = {
        "화토동법": "戊·己는 丙·丁과 같은 십이운성(다수설)",
        "십이신살기준": "년지·일지 병기(sinsalFromYear·sinsalFromDay)",
        "양인": "양간(甲丙戊庚壬) 정설 — 음간은 미포함",
        "공망": "일주 순중공망(旬中空亡)",
        "지장간가중": "withHidden은 지장간 전부 각 1로 집계",
        "신강신약": "득령·득지·득세 사실만 — 점수·최종판정 없음(다수설 참고라벨)",
        "격국": "월지 투출 우선, 없으면 월령 본기 — 단정 없이 후보만",
        "용신": "억부(참고판정 기준)+조후(계절 한난 개략) 후보만",
    }
    return out
