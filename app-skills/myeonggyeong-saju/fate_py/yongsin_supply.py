"""용신 공급(用神 供給) 교차 — fate-js src/match/yongsin-supply.ts 1:1 미러링.

상대 원국이 내 희신을 얼마나·어떻게 공급하는가 (yongsinSupply).
"""

from .analysis import analysis_facts
from .constants import STEM_ELEMENTS, BRANCH_ELEMENTS, HIDDEN_STEMS, CONTROLS

EL_KO = {"wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"}


def _partner_elements(partner: dict) -> dict:
    """상대 원국의 오행 — visible=천간 4자(투출), grounded=천간+지지 본기."""
    cells_ = [c for c in (partner["year"], partner["month"], partner["day"], partner.get("hour")) if c is not None]
    visible = set(STEM_ELEMENTS[c["stem"]] for c in cells_)
    grounded = set(visible) | set(BRANCH_ELEMENTS[c["branch"]] for c in cells_)
    visible_stems = set(c["stem"] for c in cells_)
    all_stems = set(visible_stems)
    for c in cells_:
        for hs in HIDDEN_STEMS[c["branch"]]:
            all_stems.add(hs)
    return {"visible": visible, "grounded": grounded, "visibleStems": visible_stems, "allStems": all_stems}


def _eokbu_supply_judgment(id_, me_label, partner_label, partner, favorable) -> dict:
    p = _partner_elements(partner)
    covered = [e for e in favorable if e in p["grounded"]]
    revealed = [e for e in favorable if e in p["visible"]]
    present = len(covered) > 0
    fav_str = "".join(EL_KO[e] for e in favorable)
    cov_str = "".join(EL_KO[e] for e in covered)
    rev_str = "".join(EL_KO[e] for e in revealed)
    return {
        "id": id_, "label": f"{me_label} 억부용신 공급", "category": f"{len(covered)}/{len(favorable)}", "present": present,
        "statement": (
            f"{me_label} 억부 희신 {fav_str} 중 {partner_label} 원국이 {cov_str}을(를) 공급"
            + (f" — {rev_str}은(는) 천간 투출." if revealed else " — 투출 없음(지지·본기).")
            if present else
            f"{partner_label} 원국은 {me_label} 억부 희신 {fav_str}을(를) 공급하지 않음."
        ),
        "source": "억부용신 공급",
        "detail": {
            "favorable": [EL_KO[e] for e in favorable],
            "covered": [EL_KO[e] for e in covered],
            "revealed": [EL_KO[e] for e in revealed],
        },
    }


def _johu_supply_judgment(id_, me_label, partner_label, partner, main, sub) -> dict:
    p = _partner_elements(partner)
    main_revealed = [s for s in main if s in p["visibleStems"]]
    main_hidden = [s for s in main if s not in p["visibleStems"] and s in p["allStems"]]
    sub_hit = [s for s in sub if s in p["allStems"]]
    present = len(main_revealed) > 0 or len(main_hidden) > 0
    return {
        "id": id_, "label": f"{me_label} 조후용신 공급",
        "category": "투출" if len(main_revealed) > 0 else ("암장" if present else False),
        "present": present,
        "statement": (
            f"{me_label} 조후 主用神 {''.join(main)} 중 "
            + ", ".join([s for s in (
                (f"{''.join(main_revealed)}이(가) {partner_label} 천간에 투출" if main_revealed else ""),
                (f"{''.join(main_hidden)}은(는) 지장간에만 암장" if main_hidden else ""),
            ) if s])
            + (f" (次佐 {''.join(sub_hit)}도 있음)." if sub_hit else ".")
            if present else
            f"{partner_label} 원국은 {me_label} 조후 主用神 {''.join(main)}을(를) 갖고 있지 않음."
        ),
        "source": "조후용신 공급(궁통보감 표)",
        "detail": {"main": main, "sub": sub, "mainRevealed": main_revealed, "mainHidden": main_hidden, "subHit": sub_hit},
    }


def _harm_judgment(id_, me_label, partner_label, partner, unfavorable, favorable) -> dict:
    p = _partner_elements(partner)
    covered = [e for e in unfavorable if e in p["grounded"]]
    revealed = [e for e in unfavorable if e in p["visible"]]
    keuk = []
    for c in (partner["year"], partner["month"], partner["day"], partner.get("hour")):
        if c is None:
            continue
        el = STEM_ELEMENTS[c["stem"]]
        hit = next((f for f in favorable if CONTROLS[el] == f), None)
        if hit:
            keuk.append(f"{c['stem']}剋{EL_KO[hit]}")
    # [...new Set(keuk)] — 삽입 순서 보존 dedup.
    keuk_uniq = list(dict.fromkeys(keuk))
    present = len(covered) > 0 or len(keuk_uniq) > 0
    unf_str = "".join(EL_KO[e] for e in unfavorable)
    cov_str = "".join(EL_KO[e] for e in covered)
    rev_str = "".join(EL_KO[e] for e in revealed)
    return {
        "id": id_, "label": f"{me_label} 기신 유입·용신 극",
        "category": "투출" if len(revealed) > 0 else ("암장" if present else False),
        "present": present,
        "statement": (
            " ".join([s for s in (
                (
                    f"{me_label} 억부 기신 {unf_str} 중 {partner_label} 원국이 {cov_str}을(를) 유입"
                    + (f" — {rev_str}은(는) 천간 투출." if revealed else " — 투출 없음(지지·본기).")
                    if covered else ""
                ),
                (f"{partner_label} 천간이 {me_label} 희신을 극: {'·'.join(keuk_uniq)}." if keuk_uniq else ""),
            ) if s])
            if present else
            f"{partner_label} 원국은 {me_label} 기신 {unf_str}을(를) 유입시키지 않고 희신을 극하지도 않음."
        ),
        "source": "억부용신 공급(거울면)",
        "detail": {
            "unfavorable": [EL_KO[e] for e in unfavorable],
            "covered": [EL_KO[e] for e in covered],
            "revealed": [EL_KO[e] for e in revealed],
            "keuk": keuk_uniq,
        },
    }


def yongsin_supply(subject: dict, candidate: dict) -> dict:
    a = analysis_facts(subject["bazi"])["yongsin"]
    b = analysis_facts(candidate["bazi"])["yongsin"]
    return {
        "eokbuToSubject": _eokbu_supply_judgment("yongsin_eokbu_subject", "주체", "후보", candidate["bazi"], a["eokbu"]["favorable"]),
        "eokbuToCandidate": _eokbu_supply_judgment("yongsin_eokbu_candidate", "후보", "주체", subject["bazi"], b["eokbu"]["favorable"]),
        "johuToSubject": _johu_supply_judgment("johu_subject", "주체", "후보", candidate["bazi"], a["johu"]["main"], a["johu"]["sub"]),
        "johuToCandidate": _johu_supply_judgment("johu_candidate", "후보", "주체", subject["bazi"], b["johu"]["main"], b["johu"]["sub"]),
        "harmToSubject": _harm_judgment("yongsin_harm_subject", "주체", "후보", candidate["bazi"], a["eokbu"]["unfavorable"], a["eokbu"]["favorable"]),
        "harmToCandidate": _harm_judgment("yongsin_harm_candidate", "후보", "주체", subject["bazi"], b["eokbu"]["unfavorable"], b["eokbu"]["favorable"]),
    }
