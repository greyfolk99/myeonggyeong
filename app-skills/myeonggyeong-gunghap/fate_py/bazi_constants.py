"""1인 원국 파생 상수 — fate-js src/bazi/constants.ts 1:1 미러링.

십이운성(十二運星)·십이신살(十二神殺).
"""

from .constants import BRANCH_INDEX, STEM_YINYANG
from .match_constants import BRANCH_SAMHAP

# 십이운성 12단계 — 장생지에서 진행 순서.
TWELVE_STAGES = (
    "장생(長生)", "목욕(沐浴)", "관대(冠帶)", "임관(臨官)",
    "제왕(帝旺)", "쇠(衰)", "병(病)", "사(死)",
    "묘(墓)", "절(絕)", "태(胎)", "양(養)",
)

# 일간별 장생지(長生地) — 화토동법.
JANGSAENG_BY_STEM = {
    "甲": "亥", "乙": "午",
    "丙": "寅", "丁": "酉",
    "戊": "寅", "己": "酉",
    "庚": "巳", "辛": "子",
    "壬": "申", "癸": "卯",
}


def twelve_stage(day_stem: str, branch: str) -> str:
    """일간 기준 지지 하나의 십이운성 단계. 양간 순행(+), 음간 역행(-)."""
    jang = BRANCH_INDEX[JANGSAENG_BY_STEM[day_stem]]
    b = BRANCH_INDEX[branch]
    forward = STEM_YINYANG[day_stem] == "yang"
    idx = (b - jang + 12) % 12 if forward else (jang - b + 12) % 12
    return TWELVE_STAGES[idx]


# 십이신살 12종 — 겁살부터 순서.
TWELVE_SINSAL = (
    "겁살(劫殺)", "재살(災殺)", "천살(天殺)", "지살(地殺)",
    "년살(年殺)", "월살(月殺)", "망신살(亡神殺)", "장성살(將星殺)",
    "반안살(攀鞍殺)", "역마살(驛馬殺)", "육해살(六害殺)", "화개살(華蓋殺)",
)


# 지지 → 자신이 속한 삼합국의 장생지(長生地).
def _build_jangsaeng_of_group():
    start_by_element = {"water": "申", "wood": "亥", "fire": "寅", "metal": "巳"}
    out = {}
    for g in BRANCH_SAMHAP:
        start = start_by_element[g["element"]]
        for b in g["branches"]:
            out[b] = start
    return out


_JANGSAENG_OF_GROUP = _build_jangsaeng_of_group()


def twelve_sinsal(ref: str, branch: str) -> str:
    """기준지 ref 를 기준으로 지지 branch 가 갖는 십이신살 명칭."""
    jang = BRANCH_INDEX[_JANGSAENG_OF_GROUP[ref]]  # 지살 자리
    start = (jang - 3 + 12) % 12  # 겁살 자리
    idx = (BRANCH_INDEX[branch] - start + 12) % 12
    return TWELVE_SINSAL[idx]
