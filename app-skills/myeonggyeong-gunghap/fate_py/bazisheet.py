"""baziSheet — fate-js src/bazi/bazisheet.ts 1:1 미러링.

한 사람의 원국+분석 시트(한자 코드 머신키·present-only). baziSheet·toBaziSheet·formatBaziSheet.
"""

import re

from .analyze import analyze

BAZISHEET_SCHEMA_VERSION = "bazi-sheet-v2"
BAZISHEET_POLICY_VERSION = "bazi-sheet/2026-09"

# ── 코드 맵(머신키) ─────────────────────────────────────────────────

_EL = {"wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"}
_YY = {"yang": "陽", "yin": "陰"}
_TG = {
    "비견": "比肩", "겁재": "劫財", "식신": "食神", "상관": "傷官", "편재": "偏財",
    "정재": "正財", "편관": "偏官", "정관": "正官", "편인": "偏印", "정인": "正印",
}
_GRP = {"비겁": "比劫", "인성": "印星", "식상": "食傷", "재성": "財星", "관성": "官星"}
_VERDICT = {"신강": "身強", "신약": "身弱", "중화": "中和"}
_REL = {
    "stem_hap": "天干合", "stem_clash": "天干沖",
    "branch_yukhap": "地支六合", "branch_clash": "地支沖",
    "branch_hae": "害", "branch_pa": "破", "branch_wonjin": "怨嗔", "branch_hyung": "刑",
    "branch_samhap": "地支三合", "branch_samhap_ban": "地支三合半合",
    "branch_banghap": "地支方合", "branch_banghap_ban": "地支方合半合",
}
_SP = {
    "cheoneul": "天乙貴人", "munchang": "文昌貴人", "hongyeom": "紅艶殺",
    "yangin": "羊刃", "baekho": "白虎大殺", "gwaegang": "魁罡", "gwimun": "鬼門關殺",
}

_HANJA_RE = re.compile(r"[(（]([^)）]+)[)）]")


def _hanja(s: str) -> str:
    """'장성살(將星殺)' → '將星殺'. 괄호 안 한자만."""
    m = _HANJA_RE.search(s)
    return m.group(1) if m else s


def _el(e):
    return _EL[e]


def _yy(v):
    return _YY[v]


def _tg(g):
    return None if g is None else _TG[g]


def _map_element_count(ec: dict) -> dict:
    return {"木": ec["wood"], "火": ec["fire"], "土": ec["earth"], "金": ec["metal"], "水": ec["water"]}


def _map_group_count(g: dict) -> dict:
    return {"比劫": g["비겁"], "印星": g["인성"], "食傷": g["식상"], "財星": g["재성"], "官星": g["관성"]}


def to_bazi_sheet(n: dict) -> dict:
    """BaziAnalysis → baziSheet. 순수 함수(표현 정규화만)."""
    if len(n["pillars"]) != 4:
        raise Exception("baziSheet는 4기둥(시주 포함)이 필요합니다 — 출생시가 없으면 산출 불가")
    if not n.get("gender"):
        raise Exception("baziSheet는 gender가 필요합니다")

    s = n["analysis"]["strength"]
    g = n["analysis"]["gyeokguk"]
    y = n["analysis"]["yongsin"]

    def gyeokguk_basis():
        return "月令透出" if len(g["revealed"]) > 0 else "月令本氣"

    pillars = []
    for p in n["pillars"]:
        if not p["nayin"]:
            raise Exception(f"납음 없음(불가능한 간지): {p['ganzhi']}")
        pillars.append({
            "name": p["name"],
            "ganzhi": p["ganzhi"],
            "stem": {
                "glyph": p["stem"]["glyph"], "element": _el(p["stem"]["element"]),
                "yinyang": _yy(p["stem"]["yinyang"]), "tenGod": _tg(p["stem"]["tenGod"]),
            },
            "branch": {
                "glyph": p["branch"]["glyph"],
                "element": _el(p["branch"]["element"]),
                "yinyang": _yy(p["branch"]["yinyang"]),
                "tenGod": _tg(p["branch"]["tenGod"]),
                "hiddenStems": [
                    {
                        "glyph": h["glyph"], "element": _el(h["element"]), "yinyang": _yy(h["yinyang"]),
                        "tenGod": _tg(h["tenGod"]), "role": _hanja(h["role"]),
                    }
                    for h in p["branch"]["hiddenStems"]
                ],
                "twelveStage": _hanja(p["branch"]["twelveStage"]),
            },
            "nayin": {"name": p["nayin"]["name"], "element": _el(p["nayin"]["element"])},
        })

    ten_god_distribution = {code: n["tenGodDistribution"][ko] for ko, code in _TG.items()}

    relations = []
    for r in n["internalRelations"]:
        rel = {
            "kind": _REL.get(r["id"], r["id"]),
            "detail": (
                _hanja(r["label"].split("·")[1])
                if r["id"] == "branch_hyung" and "·" in r["label"] else None
            ),
            "polarity": r["polarity"],
            "pillars": r["pillars"],
            "glyphs": r["glyphs"],
        }
        if r.get("element"):
            rel["element"] = _el(r["element"])
        relations.append(rel)

    johu_out = {
        "season": _hanja(y["johu"]["season"]),
        "main": list(y["johu"]["main"]),
        "sub": list(y["johu"]["sub"]),
    }
    if y["johu"].get("cond"):
        johu_out["cond"] = y["johu"]["cond"]

    out = {
        "schemaVersion": BAZISHEET_SCHEMA_VERSION,
        "bazi": {
            "year": {"stem": n["bazi"]["year"]["stem"], "branch": n["bazi"]["year"]["branch"]},
            "month": {"stem": n["bazi"]["month"]["stem"], "branch": n["bazi"]["month"]["branch"]},
            "day": {"stem": n["bazi"]["day"]["stem"], "branch": n["bazi"]["day"]["branch"]},
            "hour": (
                {"stem": n["bazi"]["hour"]["stem"], "branch": n["bazi"]["hour"]["branch"]}
                if n["bazi"].get("hour") else None
            ),
        },
        "gender": n["gender"],
        "dayMaster": {
            "glyph": n["dayMaster"]["glyph"], "element": _el(n["dayMaster"]["element"]),
            "yinyang": _yy(n["dayMaster"]["yinyang"]),
        },
        "pillars": pillars,
        "tenGodDistribution": ten_god_distribution,
        "elementDistribution": {
            "simple": _map_element_count(n["elementDistribution"]["simple"]),
            "withHidden": _map_element_count(n["elementDistribution"]["withHidden"]),
        },
        "analysis": {
            "strength": {
                "dayElement": _el(s["dayElement"]),
                "deukryeong": {"present": s["deukryeong"]["present"], "monthBranchTenGod": _tg(s["deukryeong"]["monthBranchTenGod"])},
                "deukji": {"present": s["deukji"]["present"], "roots": [{"stem": r["stem"], "tenGod": _TG[r["tenGod"]]} for r in s["deukji"]["roots"]]},
                "deukse": {
                    "simple": {"ally": s["deukse"]["simple"]["ally"], "foe": s["deukse"]["simple"]["foe"], "byGroup": _map_group_count(s["deukse"]["simple"]["byGroup"])},
                    "withHidden": {"ally": s["deukse"]["withHidden"]["ally"], "foe": s["deukse"]["withHidden"]["foe"], "byGroup": _map_group_count(s["deukse"]["withHidden"]["byGroup"])},
                },
                "rooting": [{"pillar": r["pillar"], "via": [{"stem": v["stem"], "kind": _GRP[v["kind"]]} for v in r["via"]]} for r in s["rooting"]],
                "revealed": [{"stem": r["stem"], "fromBranch": r["fromBranch"], "atStems": r["atStems"]} for r in s["revealed"]],
                "byRule": [{"rule": "抑扶", "result": _VERDICT[s["reference"]["verdict"]]}],
            },
            "gyeokguk": {
                "monthBranch": g["monthBranch"],
                "monthHiddenStems": [{"stem": h["stem"], "tenGod": _TG[h["tenGod"]], "role": _hanja(h["role"])} for h in g["monthHiddenStems"]],
                "revealed": [{"stem": r["stem"], "tenGod": _TG[r["tenGod"]], "role": _hanja(r["role"]), "atStems": r["atStems"]} for r in g["revealed"]],
                "candidates": [{"basedOn": _TG[c["tenGod"]], "basis": gyeokguk_basis()} for c in g["candidates"]],
            },
            "yongsin": {
                "eokbu": {"favorable": [_el(e) for e in y["eokbu"]["favorable"]], "unfavorable": [_el(e) for e in y["eokbu"]["unfavorable"]]},
                "johu": johu_out,
            },
            "relations": relations,
            "void": n["voidBranches"],
        },
        "twelveSinsal": {
            "fromYear": [_hanja(p["branch"]["sinsalFromYear"]) for p in n["pillars"]],
            "fromDay": [_hanja(p["branch"]["sinsalFromDay"]) for p in n["pillars"]],
        },
        "specialSinsal": [
            {"code": _SP.get(x["id"], x["id"]), "pillars": x["pillars"]}
            for x in n["sinsal"] if x["present"]
        ],
        "policyVersion": BAZISHEET_POLICY_VERSION,
    }
    return out


def bazi_sheet(subject: dict) -> dict:
    """사주 한 벌 → baziSheet(원국+분석 시트). 4기둥·성별 필수."""
    return to_bazi_sheet(analyze(subject))


def format_bazi_sheet(b: dict, tag: str = "원국") -> str:
    """baziSheet 를 한자 한 줄로 렌더."""
    el = " ".join(
        f"{k}{v}" for k, v in b["elementDistribution"]["withHidden"].items() if v > 0
    )
    st = "/".join(f"{s['rule']}:{s['result']}" for s in b["analysis"]["strength"]["byRule"]) or "—"
    yong = "".join(b["analysis"]["yongsin"]["eokbu"]["favorable"]) or "—"
    gg = ",".join(f"{g['basedOn']}({g['basis']})" for g in b["analysis"]["gyeokguk"]["candidates"]) or "—"
    vd = "".join(b["analysis"]["void"]) or "—"
    pillar_hanja = {"year": "年", "month": "月", "day": "日", "hour": "時"}
    rooting = b["analysis"]["strength"]["rooting"]
    root = "無根" if len(rooting) == 0 else "".join(pillar_hanja.get(r["pillar"], r["pillar"]) for r in rooting)
    jh = b["analysis"]["yongsin"]["johu"]
    johu = "".join(jh["main"]) + (f"({''.join(jh['sub'])})" if jh["sub"] else "")
    return (
        f"【{tag}】 {' '.join(p['ganzhi'] for p in b['pillars'])} · 일간 {b['dayMaster']['glyph']}{b['dayMaster']['element']}"
        f" · 강약 {st} · 통근 {root} · 용신 {yong} · 조후 {johu} · 오행 {el} · 격국 {gg} · 공망 {vd}"
    )
