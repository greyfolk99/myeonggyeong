"""궁합(宮合) 룰 전용 명리 상수 — fate-js src/match/constants.ts 1:1 미러링.

계산이 표로 딱 떨어지는 관계만 담는다.
"""

# 천간충(天干沖) — 甲庚·乙辛·丙壬·丁癸. (戊己 중앙토는 충하지 않는다.)
STEM_CLASH = [
    frozenset(("甲", "庚")),
    frozenset(("乙", "辛")),
    frozenset(("丙", "壬")),
    frozenset(("丁", "癸")),
]

# 삼합(三合) — BranchGroup: {branches, king, element}.
BRANCH_SAMHAP = [
    {"branches": ("申", "子", "辰"), "king": "子", "element": "water"},
    {"branches": ("亥", "卯", "未"), "king": "卯", "element": "wood"},
    {"branches": ("寅", "午", "戌"), "king": "午", "element": "fire"},
    {"branches": ("巳", "酉", "丑"), "king": "酉", "element": "metal"},
]

# 방합(方合).
BRANCH_BANGHAP = [
    {"branches": ("寅", "卯", "辰"), "king": "卯", "element": "wood"},
    {"branches": ("巳", "午", "未"), "king": "午", "element": "fire"},
    {"branches": ("申", "酉", "戌"), "king": "酉", "element": "metal"},
    {"branches": ("亥", "子", "丑"), "king": "子", "element": "water"},
]

# 형(刑) — HyungRule: {branches, kind, name}. kind = samhyung|sanghyung|jahyung.
BRANCH_HYUNG = [
    {"branches": ("寅", "巳", "申"), "kind": "samhyung", "name": "무은지형(無恩之刑)"},
    {"branches": ("丑", "戌", "未"), "kind": "samhyung", "name": "시세지형(恃勢之刑)"},
    {"branches": ("子", "卯"), "kind": "sanghyung", "name": "무례지형(無禮之刑)"},
    {"branches": ("辰", "辰"), "kind": "jahyung", "name": "진진자형(辰辰自刑)"},
    {"branches": ("午", "午"), "kind": "jahyung", "name": "오오자형(午午自刑)"},
    {"branches": ("酉", "酉"), "kind": "jahyung", "name": "유유자형(酉酉自刑)"},
    {"branches": ("亥", "亥"), "kind": "jahyung", "name": "해해자형(亥亥自刑)"},
]

# 파(破) — 육파(六破). 子酉·午卯·申巳·寅亥·辰丑·戌未.
BRANCH_PA = [
    frozenset(("子", "酉")),
    frozenset(("午", "卯")),
    frozenset(("申", "巳")),
    frozenset(("寅", "亥")),
    frozenset(("辰", "丑")),
    frozenset(("戌", "未")),
]

# 원진(怨嗔) — 子未·丑午·寅酉·卯申·辰亥·巳戌.
BRANCH_WONJIN = [
    frozenset(("子", "未")),
    frozenset(("丑", "午")),
    frozenset(("寅", "酉")),
    frozenset(("卯", "申")),
    frozenset(("辰", "亥")),
    frozenset(("巳", "戌")),
]
