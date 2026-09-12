"""궁합 시트 — fate-js src/match/matchsheet.ts 1:1 미러링.

matchSheet·formatMatchSheet. MATCHSHEET_SCHEMA_VERSION.
"""

import re

from .rules import (
    cells,
    pairwise_rules,
    hyung_rule,
    samhap_rule,
    banghap_rule,
    hidden_amhap_rule,
    element_complement_rule,
)
from .judgments import judge_match
from .yongsin_supply import yongsin_supply
from .constants import STEM_ELEMENTS, GENERATES, CONTROLS

MATCHSHEET_SCHEMA_VERSION = "match-sheet-v2"

# match fact id → 렌즈 매핑.
_FACT_LENS = {
    "stem_hap": "合",
    "branch_yukhap": "合",
    "branch_samhap": "合",
    "branch_banghap": "合",
    "hidden_amhap": "合",
    "element_complement": "生",
    "stem_clash": "沖",
    "branch_clash": "沖",
    "branch_hae": "沖",
    "branch_pa": "沖",
    "branch_wonjin": "沖",
    "branch_hyung": "沖",
}

_LENS_ORDER = ["合", "生", "沖"]


def match_sheet(subject: dict, candidate: dict) -> dict:
    """두 사주 사이의 명리 관계를 정형 포맷으로 추출한다."""
    s = cells(subject["bazi"])
    c = cells(candidate["bazi"])

    facts = [
        *pairwise_rules(s, c),
        hyung_rule(s, c),
        samhap_rule(s, c),
        banghap_rule(s, c),
        hidden_amhap_rule(s, c),
        element_complement_rule(s, c),
    ]

    judgments = {
        **judge_match(subject, candidate, facts),
        "yongsinSupply": yongsin_supply(subject, candidate),
    }

    lenses = []
    for lens in _LENS_ORDER:
        group = [f for f in facts if _FACT_LENS.get(f["id"]) == lens]
        lenses.append({
            "lens": lens,
            "facts": group,
            "activeCount": len([f for f in group if f["present"]]),
            "edgeTotal": sum(f["count"] for f in group),
        })

    return {
        "schemaVersion": MATCHSHEET_SCHEMA_VERSION,
        "subject": subject,
        "candidate": candidate,
        "facts": facts,
        "lenses": lenses,
        "judgments": judgments,
    }


_ELEMENT_HANJA = {"wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"}

_LENS_NAME = {
    "合": "合(끌림·정)",
    "生": "生(보완·상생)",
    "沖": "沖(관계온도)",
}

_NAYIN_RELATION_HANJA = {"same": "比和", "generates": "相生", "controls": "相剋"}

_FACT_HANJA = {
    "stem_hap": "天干合", "stem_clash": "天干沖",
    "branch_yukhap": "六合", "branch_clash": "六沖", "branch_hae": "六害", "branch_pa": "六破",
    "branch_wonjin": "怨嗔", "branch_hyung": "刑", "branch_samhap": "三合", "branch_banghap": "方合",
    "hidden_amhap": "暗合", "element_complement": "五行相補",
}
_SINSAL_HANJA = {
    "dohwa": "桃花", "yeokma": "驛馬", "hwagae": "華蓋", "hongyeom": "紅艶",
    "cheoneul": "天乙貴人", "munchang": "文昌貴人", "yangin": "羊刃",
    "baekho": "白虎", "gwaegang": "魁罡", "gwimun": "鬼門關殺",
}

_PAREN_RE = re.compile(r"\(([^)]+)\)")


def _hanja_of(label: str) -> str:
    m = _PAREN_RE.search(label)
    return m.group(1) if m else label


def _els_hanja(lst) -> str:
    if not isinstance(lst, list):
        return ""
    return "".join(_ELEMENT_HANJA.get(e, str(e)) for e in lst)


_PILLAR_HANJA = {"year": "年", "month": "月", "day": "日", "hour": "時"}


def _edge_hanja(e: dict) -> str:
    return f"A{_PILLAR_HANJA[e['subject']['pillar']]}{e['subject']['glyph']}-B{_PILLAR_HANJA[e['object']['pillar']]}{e['object']['glyph']}"


def _group_segments(name: str, edges: list) -> list:
    by_el = {}
    for e in edges:
        el = _ELEMENT_HANJA.get(e["element"], str(e["element"]))
        by_el.setdefault(el, []).append(e)
    out = []
    for el, es in by_el.items():
        glyphs = set()
        for e in es:
            glyphs.add(e["subject"]["glyph"])
            glyphs.add(e["object"]["glyph"])
        size = "三字" if len(glyphs) >= 3 else "二字"
        out.append(f"{name}({el}·{size})[{' '.join(_edge_hanja(e) for e in es)}]")
    return out


_SAMHYUNG_GROUPS = {
    "無恩之刑": ["寅", "巳", "申"],
    "恃勢之刑": ["丑", "戌", "未"],
}


def format_match_sheet(sheet: dict, opts: dict = None) -> str:
    """궁합 시트를 한자 텍스트 블록으로 렌더한다."""
    opts = opts or {}
    lines = []
    for g in sheet["lenses"]:
        active = [f for f in g["facts"] if f["present"]]
        parts = []
        for f in active:
            name = _FACT_HANJA.get(f["id"]) or _hanja_of(f["label"])
            if f["id"] == "element_complement":
                extra = ""
                if f.get("detail"):
                    a = _els_hanja(f["detail"].get("subjectReceives"))
                    b = _els_hanja(f["detail"].get("candidateReceives"))
                    segs = [x for x in (f"A受{a}" if a else "", f"B受{b}" if b else "") if x]
                    if segs:
                        extra = f"({' '.join(segs)})"
                parts.append(f"{name}{extra}")
                continue
            if f["id"] == "branch_samhap" or f["id"] == "branch_banghap":
                parts.extend(_group_segments(name, f["edges"]))
                continue
            if f["id"] == "branch_hyung" and isinstance((f.get("detail") or {}).get("hyung"), list):
                kind_parts = []
                for k in f["detail"]["hyung"]:
                    group = _SAMHYUNG_GROUPS.get(k)
                    if not group:
                        kind_parts.append(k)
                        continue
                    glyphs = set()
                    for e in f["edges"]:
                        for gph in (e["subject"]["glyph"], e["object"]["glyph"]):
                            if gph in group:
                                glyphs.add(gph)
                    kind_parts.append(f"{k}({'三字' if len(glyphs) >= 3 else '二字'})")
                kinds = f"({'·'.join(kind_parts)})"
            else:
                kinds = ""
            parts.append(f"{name}{kinds}[{' '.join(_edge_hanja(e) for e in f['edges'])}]")

        if g["lens"] == "生":
            tg = sheet["judgments"]["tenGod"]

            def star(jd, tag):
                if not jd["present"]:
                    parts.append(f"{tag}(無)")
                    return
                d = jd["detail"]
                segs = [x for x in (
                    (f"{''.join(_PILLAR_HANJA[p] for p in d['revealedPillars'])}透" if d["revealedPillars"] else "藏"),
                    (("坐日支" if d["daySeat"] == "본기" else "日支藏") if d["daySeat"] else ""),
                    f"正{d['jeong']}偏{d['pyeon']}",
                ) if x]
                parts.append(f"{tag}({'·'.join(segs)})")

            star(tg["spouseStarForSubject"], "配星A←B")
            star(tg["spouseStarForCandidate"], "配星B←A")
            ys = sheet["judgments"]["yongsinSupply"]

            def eokbu(jd, tag):
                if not jd["present"]:
                    parts.append(f"{tag}(無)")
                    return
                d = jd["detail"]
                rev = f"·{''.join(d['revealed'])}透" if d["revealed"] else "·無透"
                parts.append(f"{tag}({''.join(d['covered'])}/{''.join(d['favorable'])}供{rev})")

            eokbu(ys["eokbuToSubject"], "用神A←B")
            eokbu(ys["eokbuToCandidate"], "用神B←A")

            def johu(jd, tag):
                d = jd["detail"]
                seg = "·".join([x for x in (
                    (f"{''.join(d['mainRevealed'])}透" if d["mainRevealed"] else ""),
                    (f"{''.join(d['mainHidden'])}藏" if d["mainHidden"] else ""),
                ) if x]) or "無"
                jwa = f"·佐{''.join(d['subHit'])}" if d.get("subHit") else ""
                parts.append(f"{tag}({seg}{jwa})")

            johu(ys["johuToSubject"], "調候A←B")
            johu(ys["johuToCandidate"], "調候B←A")
            if opts.get("includeHarm"):
                def harm(jd, tag, keuk_tag):
                    d = jd["detail"]
                    if d["covered"]:
                        rev = f"·{''.join(d['revealed'])}透" if d["revealed"] else "·無透"
                        parts.append(f"{tag}({''.join(d['covered'])}/{''.join(d['unfavorable'])}入{rev})")
                    else:
                        parts.append(f"{tag}(無)")
                    parts.append(f"{keuk_tag}({'·'.join(d['keuk'])})" if d["keuk"] else f"{keuk_tag}(無)")

                harm(ys["harmToSubject"], "忌神A←B", "剋用神A←B")
                harm(ys["harmToCandidate"], "忌神B←A", "剋用神B←A")
        lines.append(f"【{_LENS_NAME[g['lens']]}】 {' · '.join(parts) if parts else '(없음)'}")

    j = sheet["judgments"]
    if opts.get("includeWangswe") and j["chungWangswe"]["present"]:
        entries = (j["chungWangswe"].get("detail") or {}).get("entries", [])
        lines.append(f"【沖旺衰】 {' · '.join(entries)}")
    aux = []
    if j["nayin"]["outerReading"]["present"]:
        cat = str(j["nayin"]["outerReading"]["category"])
        aux.append(f"納音겉궁합:{_NAYIN_RELATION_HANJA.get(cat, cat)}")
    if j["palace"]["present"]:
        d = j["palace"].get("detail") or {}
        aux.append(
            f"궁위 겉(和{d.get('outerHarmony', 0)}沖{d.get('outerClash', 0)})"
            f"속(和{d.get('innerHarmony', 0)}沖{d.get('innerClash', 0)})"
        )
    s2 = [_SINSAL_HANJA.get(s["id"]) or _hanja_of(s["label"]) for s in j["sinsal"]["candidateForSubject"] if s["present"]]
    s1 = [_SINSAL_HANJA.get(s["id"]) or _hanja_of(s["label"]) for s in j["sinsal"]["subjectForCandidate"] if s["present"]]
    if s2:
        aux.append(f"神殺(B→A):{'·'.join(s2)}")
    if s1:
        aux.append(f"神殺(A→B):{'·'.join(s1)}")
    if aux:
        lines.append(f"【보조】 {' · '.join(aux)}")

    cr = j["cross"]
    cx = []
    ds_a = sheet["subject"]["bazi"]["day"]["stem"]
    ds_b = sheet["candidate"]["bazi"]["day"]["stem"]
    e_a = STEM_ELEMENTS[ds_a]
    e_b = STEM_ELEMENTS[ds_b]
    if e_a == e_b:
        day_stem_rel = f"比和({ds_a}·{ds_b})"
    elif GENERATES[e_a] == e_b:
        day_stem_rel = f"A{ds_a}生B{ds_b}"
    elif GENERATES[e_b] == e_a:
        day_stem_rel = f"B{ds_b}生A{ds_a}"
    elif CONTROLS[e_a] == e_b:
        day_stem_rel = f"A{ds_a}剋B{ds_b}"
    else:
        day_stem_rel = f"B{ds_b}剋A{ds_a}"
    cx.append(f"日干:{day_stem_rel}")
    cx.append(f"배우자궁운성 B→A:{(cr['spouseGungStageForSubject'].get('detail') or {}).get('stage', '')}")
    cx.append(f"A→B:{(cr['spouseGungStageForCandidate'].get('detail') or {}).get('stage', '')}")
    if cr["voidForSubject"]["present"]:
        cx.append("空亡:B일지↦A공망")
    if cr["voidForCandidate"]["present"]:
        cx.append("空亡:A일지↦B공망")
    if cr["dayPillarMatch"]["present"]:
        cx.append(f"일주:{cr['dayPillarMatch']['category']}")
    cx.append(f"神殺 A년지기준B일지:{cr['sinsalCrossForSubject']['category']}")
    cx.append(f"B년지기준A일지:{cr['sinsalCrossForCandidate']['category']}")
    lines.append(f"【교차】 {' · '.join(cx)}")

    ov = j["hapChungOverlap"]
    if ov["present"]:
        overlap_cells = (ov.get("detail") or {}).get("cells", [])
        lines.append(f"【병존】 {' · '.join(overlap_cells)}")

    jh = j["jaenghap"]
    if jh["present"]:
        jaeng_cells = (jh.get("detail") or {}).get("cells", [])
        lines.append(f"【쟁합】 {' · '.join(jaeng_cells)}")

    return "\n".join(lines)
