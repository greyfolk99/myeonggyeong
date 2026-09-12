"""궁합 판단(判斷)용 명리 상수 — fate-js src/match/judgments-constants.ts 1:1 미러링.

납음·신살 룩업 테이블.
"""

# 60갑자 → 30 납음오행(納音五行). 인덱스 k(0..29) = 60간지 순번 2k, 2k+1 짝.
NAYIN_PAIRS = [
    {"name": "海中金", "element": "metal"},   # 甲子·乙丑
    {"name": "爐中火", "element": "fire"},     # 丙寅·丁卯
    {"name": "大林木", "element": "wood"},     # 戊辰·己巳
    {"name": "路傍土", "element": "earth"},    # 庚午·辛未
    {"name": "劍鋒金", "element": "metal"},    # 壬申·癸酉
    {"name": "山頭火", "element": "fire"},     # 甲戌·乙亥
    {"name": "澗下水", "element": "water"},    # 丙子·丁丑
    {"name": "城頭土", "element": "earth"},    # 戊寅·己卯
    {"name": "白蠟金", "element": "metal"},    # 庚辰·辛巳
    {"name": "楊柳木", "element": "wood"},     # 壬午·癸未
    {"name": "泉中水", "element": "water"},    # 甲申·乙酉
    {"name": "屋上土", "element": "earth"},    # 丙戌·丁亥
    {"name": "霹靂火", "element": "fire"},     # 戊子·己丑
    {"name": "松柏木", "element": "wood"},     # 庚寅·辛卯
    {"name": "長流水", "element": "water"},    # 壬辰·癸巳
    {"name": "沙中金", "element": "metal"},    # 甲午·乙未
    {"name": "山下火", "element": "fire"},     # 丙申·丁酉
    {"name": "平地木", "element": "wood"},     # 戊戌·己亥
    {"name": "壁上土", "element": "earth"},    # 庚子·辛丑
    {"name": "金箔金", "element": "metal"},    # 壬寅·癸卯
    {"name": "覆燈火", "element": "fire"},     # 甲辰·乙巳
    {"name": "天河水", "element": "water"},    # 丙午·丁未
    {"name": "大驛土", "element": "earth"},    # 戊申·己酉
    {"name": "釵釧金", "element": "metal"},    # 庚戌·辛亥
    {"name": "桑柘木", "element": "wood"},     # 壬子·癸丑
    {"name": "大溪水", "element": "water"},    # 甲寅·乙卯
    {"name": "沙中土", "element": "earth"},    # 丙辰·丁巳
    {"name": "天上火", "element": "fire"},     # 戊午·己未
    {"name": "石榴木", "element": "wood"},     # 庚申·辛酉
    {"name": "大海水", "element": "water"},    # 壬戌·癸亥
]

# 삼합(三合) 그룹별 도화(桃花)·역마(驛馬)·화개(華蓋) 지지 — 지지→값 매핑.
SINSAL_FROM_SAMHAP = {}
for _g in (
    {"members": ("申", "子", "辰"), "dohwa": "酉", "yeokma": "寅", "hwagae": "辰"},
    {"members": ("亥", "卯", "未"), "dohwa": "子", "yeokma": "巳", "hwagae": "未"},
    {"members": ("寅", "午", "戌"), "dohwa": "卯", "yeokma": "申", "hwagae": "戌"},
    {"members": ("巳", "酉", "丑"), "dohwa": "午", "yeokma": "亥", "hwagae": "丑"},
):
    for _m in _g["members"]:
        SINSAL_FROM_SAMHAP[_m] = {
            "dohwa": _g["dohwa"], "yeokma": _g["yeokma"], "hwagae": _g["hwagae"],
        }

# 홍염살(紅艶殺) — 일간 기준.
HONGYEOM_BY_STEM = {
    "甲": "午", "乙": "午",
    "丙": "寅", "丁": "未",
    "戊": "辰", "己": "辰",
    "庚": "戌", "辛": "酉",
    "壬": "子", "癸": "申",
}

# 천을귀인(天乙貴人) — 일간 기준, 각 2지.
CHEONEUL_BY_STEM = {
    "甲": ("丑", "未"),
    "乙": ("子", "申"),
    "丙": ("亥", "酉"),
    "丁": ("亥", "酉"),
    "戊": ("丑", "未"),
    "己": ("子", "申"),
    "庚": ("丑", "未"),
    "辛": ("午", "寅"),
    "壬": ("巳", "卯"),
    "癸": ("巳", "卯"),
}

# 문창귀인(文昌貴人) — 일간 기준.
MUNCHANG_BY_STEM = {
    "甲": "巳", "乙": "午",
    "丙": "申", "丁": "酉",
    "戊": "申", "己": "酉",
    "庚": "亥", "辛": "子",
    "壬": "寅", "癸": "卯",
}

# 양인살(羊刃/陽刃) — 일간 기준. 양간 5개 정설 + 음인 참고값.
YANGIN_BY_STEM = {
    "甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子",
    "乙": "辰", "丁": "未", "己": "未", "辛": "戌", "癸": "丑",
}

# 백호살(白虎大殺) — 특정 60갑자 7주.
BAEKHO_PILLARS = frozenset(("甲辰", "乙未", "丙戌", "丁丑", "戊辰", "壬戌", "癸丑"))

# 괴강살(魁罡) — 정설 4주.
GWAEGANG_PILLARS = frozenset(("庚辰", "庚戌", "壬辰", "戊戌"))

# 귀문관살(鬼門關殺) — 지지 쌍 6종.
GWIMUN_PAIRS = [
    frozenset(("子", "酉")),
    frozenset(("丑", "午")),
    frozenset(("寅", "未")),
    frozenset(("卯", "申")),
    frozenset(("辰", "亥")),
    frozenset(("巳", "戌")),
]
