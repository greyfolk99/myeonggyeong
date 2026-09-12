"""궁합 교차 판단 — fate-js src/match/crosses.ts 1:1 미러링.

두 사주의 일간·일지·년지·일주를 맞대어 나오는 결정론 사실.
"""

from .constants import BRANCHES, STEM_INDEX, BRANCH_INDEX
from .bazi_constants import twelve_stage, twelve_sinsal

PILLAR_KO = {"year": "년", "month": "월", "day": "일", "hour": "시"}


def _void_branches(bazi: dict) -> list:
    """순중공망(旬中空亡) — 일주 기준 공망 2지."""
    base = (BRANCH_INDEX[bazi["day"]["branch"]] - STEM_INDEX[bazi["day"]["stem"]] + 12) % 12
    return [BRANCHES[(base + 10) % 12], BRANCHES[(base + 11) % 12]]


def _spouse_gung_stage(id_, me_label, partner_label, me, partner) -> dict:
    stage = twelve_stage(partner["day"]["stem"], me["day"]["branch"])
    return {
        "id": id_,
        "label": f"{me_label} 배우자궁 십이운성",
        "category": stage,
        "present": True,
        "statement": f"{partner_label} 일간 {partner['day']['stem']}이(가) {me_label} 일지 {me['day']['branch']}(배우자궁)에서 십이운성 {stage}.",
        "source": "십이운성(화토동법)",
        "detail": {"partnerDayStem": partner["day"]["stem"], "myDayBranch": me["day"]["branch"], "stage": stage},
    }


def _void_cross(id_, me_label, partner_label, me, partner) -> dict:
    voids = _void_branches(me)
    hit = partner["day"]["branch"] in voids
    return {
        "id": id_,
        "label": f"{me_label} 공망 교차",
        "category": hit,
        "present": hit,
        "statement": (
            f"{me_label} 순중공망 {'·'.join(voids)}에 {partner_label} 일지 {partner['day']['branch']}이(가) 듦."
            if hit else
            f"{partner_label} 일지 {partner['day']['branch']}은(는) {me_label} 순중공망({'·'.join(voids)})에 들지 않음."
        ),
        "source": "순중공망(旬中空亡)",
        "detail": {"voids": voids, "hit": hit},
    }


def _day_pillar_match(id_, a, b) -> dict:
    a_stem, a_br = a["day"]["stem"], a["day"]["branch"]
    b_stem, b_br = b["day"]["stem"], b["day"]["branch"]
    same_stem = a_stem == b_stem
    same_branch = a_br == b_br
    if same_stem and same_branch:
        category = "동일일주"
    elif same_stem:
        category = "천간동"
    elif same_branch:
        category = "일지동"
    else:
        category = "무"
    if category == "동일일주":
        statement = f"두 일주가 {a_stem}{a_br}로 동일."
    elif category == "천간동":
        statement = f"두 일간이 {a_stem}로 같고 일지({a_br}/{b_br})는 다름."
    elif category == "일지동":
        statement = f"두 일지가 {a_br}로 같고 일간({a_stem}/{b_stem})은 다름."
    else:
        statement = f"두 일주 천간·지지 모두 다름({a_stem}{a_br}/{b_stem}{b_br})."
    return {
        "id": id_, "label": "일주 대조", "category": category, "present": category != "무",
        "statement": statement, "source": "일주 대조", "detail": {"sameStem": same_stem, "sameBranch": same_branch},
    }


def _sinsal_cross(id_, me_label, partner_label, me, partner) -> dict:
    ref = me["year"]["branch"]
    cells_ = [
        {"pillar": "year", "branch": partner["year"]["branch"]},
        {"pillar": "month", "branch": partner["month"]["branch"]},
        {"pillar": "day", "branch": partner["day"]["branch"]},
    ]
    if partner.get("hour"):
        cells_.append({"pillar": "hour", "branch": partner["hour"]["branch"]})
    mapping = [
        {"pillar": c["pillar"], "branch": c["branch"], "sinsal": twelve_sinsal(ref, c["branch"])}
        for c in cells_
    ]
    day_entry = next(m for m in mapping if m["pillar"] == "day")
    return {
        "id": id_,
        "label": f"{me_label} 년지 기준 {partner_label} 십이신살 교차",
        "category": day_entry["sinsal"],
        "present": True,
        "statement": (
            f"{me_label} 년지 {ref} 삼합국 기준 {partner_label} "
            + ", ".join(f"{PILLAR_KO[m['pillar']]}지 {m['branch']}={m['sinsal']}" for m in mapping)
            + "."
        ),
        "source": "십이신살(년지 삼합국)",
        "detail": {"ref": ref, "mappings": [f"{PILLAR_KO[m['pillar']]}:{m['branch']}:{m['sinsal']}" for m in mapping]},
    }


def cross_judgments(subject: dict, candidate: dict) -> dict:
    return {
        "spouseGungStageForSubject": _spouse_gung_stage("spouse_gung_stage_subject", "주체", "후보", subject, candidate),
        "spouseGungStageForCandidate": _spouse_gung_stage("spouse_gung_stage_candidate", "후보", "주체", candidate, subject),
        "voidForSubject": _void_cross("void_cross_subject", "주체", "후보", subject, candidate),
        "voidForCandidate": _void_cross("void_cross_candidate", "후보", "주체", candidate, subject),
        "dayPillarMatch": _day_pillar_match("day_pillar_match", subject, candidate),
        "sinsalCrossForSubject": _sinsal_cross("sinsal_cross_subject", "주체", "후보", subject, candidate),
        "sinsalCrossForCandidate": _sinsal_cross("sinsal_cross_candidate", "후보", "주체", candidate, subject),
    }
