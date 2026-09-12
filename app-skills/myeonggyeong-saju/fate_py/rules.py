"""궁합 관계 룰 — fate-js src/match/rules.ts 1:1 미러링.

cells(bazi)·renderEdge·pairwise/삼합/방합/암합/오행보완 관계 검출.
"""

from .constants import (
    STEM_COMBINATIONS,
    BRANCH_LIUHE,
    BRANCH_CLASH,
    BRANCH_HARM,
    STEM_ELEMENTS,
    BRANCH_ELEMENTS,
    HIDDEN_STEMS,
    ELEMENTS,
)
from .match_constants import (
    STEM_CLASH,
    BRANCH_PA,
    BRANCH_WONJIN,
    BRANCH_SAMHAP,
    BRANCH_BANGHAP,
    BRANCH_HYUNG,
)

# 궁(宮)의 한글 약칭 — 문장 렌더용.
PILLAR_KO = {"year": "년", "month": "월", "day": "일", "hour": "시"}

# 오행 한글 표기.
ELEMENT_KO = {
    "wood": "목(木)",
    "fire": "화(火)",
    "earth": "토(土)",
    "metal": "금(金)",
    "water": "수(水)",
}


def cells(bazi: dict) -> list:
    """사주 4주(시 미상이면 3주)를 순회 가능한 셀 배열로 편다."""
    out = [
        {"name": "year", "stem": bazi["year"]["stem"], "branch": bazi["year"]["branch"]},
        {"name": "month", "stem": bazi["month"]["stem"], "branch": bazi["month"]["branch"]},
        {"name": "day", "stem": bazi["day"]["stem"], "branch": bazi["day"]["branch"]},
    ]
    if bazi.get("hour"):
        out.append({"name": "hour", "stem": bazi["hour"]["stem"], "branch": bazi["hour"]["branch"]})
    return out


def _paired_in_sets(sets, x, y) -> bool:
    """x, y 가 sets 중 한 집합에 함께 들어가는가 (서로 다른 두 글자일 때만)."""
    if x == y:
        return False
    return any((x in s and y in s) for s in sets)


def _pillars_of(edges) -> list:
    """관여한 모든 기둥(양쪽 사주)의 합집합 — 삽입 순서 보존."""
    seen = {}
    for e in edges:
        seen[e["subject"]["pillar"]] = True
        seen[e["object"]["pillar"]] = True
    return list(seen.keys())


def _palace_note(edges) -> str:
    """일지↔일지 엣지가 있으면 '속궁합' 문구를 덧붙인다."""
    day_day = any(
        e["subject"]["pillar"] == "day" and e["object"]["pillar"] == "day" for e in edges
    )
    if day_day:
        return " 일지(배우자궁)에서 만나 속궁합에 해당한다."
    any_day = any(
        e["subject"]["pillar"] == "day" or e["object"]["pillar"] == "day" for e in edges
    )
    if any_day:
        return " 배우자궁이 관여한다."
    return ""


def _pair_rule(subject, candidate, spec) -> dict:
    edges = []
    for s in subject:
        for c in candidate:
            sg = s["stem"] if spec["accessor"] == "stem" else s["branch"]
            cg = c["stem"] if spec["accessor"] == "stem" else c["branch"]
            if _paired_in_sets(spec["sets"], sg, cg):
                edges.append({
                    "subject": {"glyph": sg, "pillar": s["name"]},
                    "object": {"glyph": cg, "pillar": c["name"]},
                })
    present = len(edges) > 0
    return {
        "id": spec["id"],
        "category": spec["accessor"],
        "label": spec["label"],
        "present": present,
        "polarity": spec["polarity"],
        "count": len(edges),
        "edges": edges,
        "pillars": _pillars_of(edges),
        "statement": (
            f"{spec['label']} {len(edges)}건." + _palace_note(edges)
            if present else spec["absent"]
        ),
        "source": spec["source"],
    }


_PAIR_SPECS = [
    {
        "id": "stem_hap", "label": "천간합(天干合)", "polarity": "harmony",
        "source": "명리약언·자평진전(천간합)", "accessor": "stem",
        "sets": STEM_COMBINATIONS, "absent": "천간합 없음.",
    },
    {
        "id": "stem_clash", "label": "천간충(天干沖)", "polarity": "clash",
        "source": "명리 통설(천간칠충)", "accessor": "stem",
        "sets": STEM_CLASH, "absent": "천간충 없음.",
    },
    {
        "id": "branch_yukhap", "label": "지지 육합(六合)", "polarity": "harmony",
        "source": "협기변방서(육합)", "accessor": "branch",
        "sets": BRANCH_LIUHE, "absent": "지지 육합 없음.",
    },
    {
        "id": "branch_clash", "label": "지지충(六沖)", "polarity": "clash",
        "source": "자평진전(육충)", "accessor": "branch",
        "sets": BRANCH_CLASH, "absent": "지지충 없음.",
    },
    {
        "id": "branch_hae", "label": "지지해(六害)", "polarity": "clash",
        "source": "명리 통설(육해)", "accessor": "branch",
        "sets": BRANCH_HARM, "absent": "지지해 없음.",
    },
    {
        "id": "branch_pa", "label": "지지파(六破)", "polarity": "clash",
        "source": "명리 통설(육파)", "accessor": "branch",
        "sets": BRANCH_PA, "absent": "지지파 없음.",
    },
    {
        "id": "branch_wonjin", "label": "원진(怨嗔)", "polarity": "clash",
        "source": "궁합 통설(원진)", "accessor": "branch",
        "sets": BRANCH_WONJIN, "absent": "원진 없음.",
    },
]


def pairwise_rules(subject, candidate) -> list:
    """pairwise 교차 룰 전체 실행."""
    return [_pair_rule(subject, candidate, spec) for spec in _PAIR_SPECS]


# 형이 성립하는 지지 쌍 → 전통 명칭. key = 정렬된 두 지지.
def _build_hyung_pairs():
    m = {}
    for rule in BRANCH_HYUNG:
        b = rule["branches"]
        for i in range(len(b)):
            for j in range(i + 1, len(b)):
                key = "".join(sorted([b[i], b[j]]))
                m[key] = rule["name"]
        first = b[0] if len(b) > 0 else None
        if rule["kind"] == "jahyung" and first:
            m[first + first] = rule["name"]
    return m


_HYUNG_PAIRS = _build_hyung_pairs()

import re

_HANJA_RE = re.compile(r"[(（]([^)）]+)[)）]")


def _hyung_hanja(name: str) -> str:
    """'무은지형(無恩之刑)' → '無恩之刑'. 괄호 안 한자 코드만 뽑는다."""
    m = _HANJA_RE.search(name)
    return m.group(1) if m else name


def hyung_rule(subject, candidate) -> dict:
    edges = []
    kinds = []
    for s in subject:
        for c in candidate:
            key = "".join(sorted([s["branch"], c["branch"]]))
            name = _HYUNG_PAIRS.get(key)
            if name:
                edges.append({
                    "subject": {"glyph": s["branch"], "pillar": s["name"]},
                    "object": {"glyph": c["branch"], "pillar": c["name"]},
                })
                code = _hyung_hanja(name)
                if code not in kinds:
                    kinds.append(code)
    present = len(edges) > 0
    out = {
        "id": "branch_hyung",
        "category": "branch",
        "label": "형(刑)",
        "present": present,
        "polarity": "clash",
        "count": len(edges),
        "edges": edges,
        "pillars": _pillars_of(edges),
        "statement": (
            f"형 {len(edges)}건({'·'.join(kinds)})." + _palace_note(edges)
            if present else "형 없음."
        ),
        "source": "자평진전·삼명통회(형)",
    }
    if present:
        out["detail"] = {"hyung": kinds}
    return out


def _group_rule(subject, candidate, groups, id_, label, source) -> dict:
    edges = []
    for g in groups:
        member_set = set(g["branches"])
        subj_members = [s for s in subject if s["branch"] in member_set]
        subj_branches = set(s["branch"] for s in subj_members)
        # 후보 지지 중 이 국의 멤버 — 주체가 이미 가진 글자(중복)는 제외.
        cand_members = [
            c for c in candidate
            if c["branch"] in member_set and c["branch"] not in subj_branches
        ]
        if len(subj_members) == 0 or len(cand_members) == 0:
            continue
        distinct = set(s["branch"] for s in subj_members) | set(c["branch"] for c in cand_members)
        if len(distinct) < 2 or g["king"] not in distinct:
            continue
        for s in subj_members:
            for c in cand_members:
                edges.append({
                    "subject": {"glyph": s["branch"], "pillar": s["name"]},
                    "object": {"glyph": c["branch"], "pillar": c["name"]},
                    "element": g["element"],
                })
    present = len(edges) > 0
    return {
        "id": id_,
        "category": "branch",
        "label": label,
        "present": present,
        "polarity": "harmony",
        "count": len(edges),
        "edges": edges,
        "pillars": _pillars_of(edges),
        "statement": (
            f"{label} 성립 — 두 사주 지지가 모여 오행 국을 이룬다." + _palace_note(edges)
            if present else f"{label} 없음."
        ),
        "source": source,
    }


def samhap_rule(subject, candidate) -> dict:
    return _group_rule(
        subject, candidate, BRANCH_SAMHAP, "branch_samhap", "삼합·반합(三合)", "연해자평(삼합)",
    )


def banghap_rule(subject, candidate) -> dict:
    return _group_rule(
        subject, candidate, BRANCH_BANGHAP, "branch_banghap", "방합(方合)", "명리 통설(방합)",
    )


def hidden_amhap_rule(subject, candidate) -> dict:
    """지장간 암합(暗合) — 지지 속 천간끼리의 은밀한 합."""
    edges = []
    for s in subject:
        for c in candidate:
            for hs in HIDDEN_STEMS[s["branch"]]:
                for hc in HIDDEN_STEMS[c["branch"]]:
                    if _paired_in_sets(STEM_COMBINATIONS, hs, hc):
                        edges.append({
                            "subject": {"glyph": hs, "pillar": s["name"]},
                            "object": {"glyph": hc, "pillar": c["name"]},
                        })
    present = len(edges) > 0
    return {
        "id": "hidden_amhap",
        "category": "hidden",
        "label": "지장간 암합(暗合)",
        "present": present,
        "polarity": "harmony",
        "count": len(edges),
        "edges": edges,
        "pillars": _pillars_of(edges),
        "statement": (
            f"지장간 암합 {len(edges)}건 — 겉으로 드러나지 않는 은근한 합." + _palace_note(edges)
            if present else "지장간 암합 없음."
        ),
        "source": "명리 통설(암합)",
    }


def _elements_present(cs) -> set:
    s = set()
    for c in cs:
        s.add(STEM_ELEMENTS[c["stem"]])
        s.add(BRANCH_ELEMENTS[c["branch"]])
    return s


def element_complement_rule(subject, candidate) -> dict:
    """오행 보완 — 한쪽에 없는 오행을 상대가 지녀 채우는 관계."""
    subj_el = _elements_present(subject)
    cand_el = _elements_present(candidate)
    subject_receives = [e for e in ELEMENTS if e not in subj_el and e in cand_el]
    candidate_receives = [e for e in ELEMENTS if e not in cand_el and e in subj_el]
    present = len(subject_receives) > 0 or len(candidate_receives) > 0

    parts = []
    if subject_receives:
        parts.append(
            f"주체에 없는 {'·'.join(ELEMENT_KO[e] for e in subject_receives)}을(를) 후보가 지녀 채운다"
        )
    if candidate_receives:
        parts.append(
            f"후보에 없는 {'·'.join(ELEMENT_KO[e] for e in candidate_receives)}을(를) 주체가 지녀 채운다"
        )

    return {
        "id": "element_complement",
        "category": "element",
        "label": "오행 보완(五行相補)",
        "present": present,
        "polarity": "harmony",
        "count": len(subject_receives) + len(candidate_receives),
        "edges": [],
        "pillars": [],
        "statement": (
            "; ".join(parts) + "."
            if present else "서로 없는 오행을 채워주는 관계 없음."
        ),
        "source": "오행 상보(통설)",
        "detail": {
            "subjectReceives": subject_receives,
            "candidateReceives": candidate_receives,
        },
    }


def render_edge(label: str, edge: dict) -> str:
    """엣지 하나를 '壬(일간) —관계— 丙(년간)' 형태로 렌더."""
    s = f"{edge['subject']['glyph']}({PILLAR_KO[edge['subject']['pillar']]})"
    o = f"{edge['object']['glyph']}({PILLAR_KO[edge['object']['pillar']]})"
    el = f" ⇒ {ELEMENT_KO[edge['element']]}" if edge.get("element") else ""
    return f"{s} —{label}— {o}{el}"
