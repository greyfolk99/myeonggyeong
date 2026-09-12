"""사주팔자 도메인 상수 — fate-js src/constants.ts 를 1:1 미러링."""

STEMS = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")

BRANCHES = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")

ELEMENTS = ("wood", "fire", "earth", "metal", "water")

STEM_INDEX = {s: i for i, s in enumerate(STEMS)}
BRANCH_INDEX = {b: i for i, b in enumerate(BRANCHES)}
ELEMENT_INDEX = {e: i for i, e in enumerate(ELEMENTS)}

STEM_ELEMENTS = {
    "甲": "wood", "乙": "wood",
    "丙": "fire", "丁": "fire",
    "戊": "earth", "己": "earth",
    "庚": "metal", "辛": "metal",
    "壬": "water", "癸": "water",
}

BRANCH_ELEMENTS = {
    "子": "water", "丑": "earth", "寅": "wood", "卯": "wood",
    "辰": "earth", "巳": "fire", "午": "fire", "未": "earth",
    "申": "metal", "酉": "metal", "戌": "earth", "亥": "water",
}

# 천간 음양(陰陽) — 甲丙戊庚壬 = 양, 乙丁己辛癸 = 음.
STEM_YINYANG = {
    "甲": "yang", "乙": "yin",
    "丙": "yang", "丁": "yin",
    "戊": "yang", "己": "yin",
    "庚": "yang", "辛": "yin",
    "壬": "yang", "癸": "yin",
}

# 지장간(地藏干) — 첫 번째 원소가 주기(主氣).
HIDDEN_STEMS = {
    "子": ("癸",),
    "丑": ("己", "癸", "辛"),
    "寅": ("甲", "丙", "戊"),
    "卯": ("乙",),
    "辰": ("戊", "乙", "癸"),
    "巳": ("丙", "戊", "庚"),
    "午": ("丁", "己"),
    "未": ("己", "丁", "乙"),
    "申": ("庚", "壬", "戊"),
    "酉": ("辛",),
    "戌": ("戊", "辛", "丁"),
    "亥": ("壬", "甲"),
}

# 천간합(天干合).
STEM_COMBINATIONS = [
    frozenset(("甲", "己")),
    frozenset(("乙", "庚")),
    frozenset(("丙", "辛")),
    frozenset(("丁", "壬")),
    frozenset(("戊", "癸")),
]

# 지지육합(地支六合).
BRANCH_LIUHE = [
    frozenset(("子", "丑")),
    frozenset(("寅", "亥")),
    frozenset(("卯", "戌")),
    frozenset(("辰", "酉")),
    frozenset(("巳", "申")),
    frozenset(("午", "未")),
]

# 지지충(地支冲).
BRANCH_CLASH = [
    frozenset(("子", "午")),
    frozenset(("丑", "未")),
    frozenset(("寅", "申")),
    frozenset(("卯", "酉")),
    frozenset(("辰", "戌")),
    frozenset(("巳", "亥")),
]

# 지지해(地支害).
BRANCH_HARM = [
    frozenset(("子", "未")),
    frozenset(("丑", "午")),
    frozenset(("寅", "巳")),
    frozenset(("卯", "辰")),
    frozenset(("申", "亥")),
    frozenset(("酉", "戌")),
]

# 오행 상생(相生) — A generates B.
GENERATES = {
    "wood": "fire",
    "fire": "earth",
    "earth": "metal",
    "metal": "water",
    "water": "wood",
}

# 오행 상극(相克) — A controls B.
CONTROLS = {
    "wood": "earth",
    "earth": "water",
    "water": "fire",
    "fire": "metal",
    "metal": "wood",
}

# 오행 피극(被克) — A is controlled by B.
CONTROLLED_BY = {
    "earth": "wood",
    "water": "earth",
    "fire": "water",
    "metal": "fire",
    "wood": "metal",
}
