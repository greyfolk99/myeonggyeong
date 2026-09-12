"""fate-py — fate-js(TypeScript 사주팔자 엔진)의 순수 파이썬 1:1 포팅.

같은 입력 → 같은 출력을 목표로 fate-js src/* 를 모듈 단위로 미러링한다.
샌드박스(외부 의존성 0, 표준 라이브러리만) 자립 실행 가능.
"""

from .bazi import bazi
from .daeun import daeun, seun
from .config import get_solar_config, set_solar_config
from . import constants
from .catalog import catalog
from .judgments import ten_god, ten_god_distribution, nayin_of, judge_match
from .analysis import analysis_facts
from .analyze import analyze
from .bazisheet import bazi_sheet, format_bazi_sheet, to_bazi_sheet
from .matchsheet import match_sheet, format_match_sheet, MATCHSHEET_SCHEMA_VERSION
from .glossary import t, label, GLOSSARY

__all__ = [
    "bazi", "daeun", "seun", "get_solar_config", "set_solar_config", "constants",
    "catalog",
    "bazi_sheet", "format_bazi_sheet", "to_bazi_sheet",
    "match_sheet", "format_match_sheet", "MATCHSHEET_SCHEMA_VERSION",
    "analysis_facts", "analyze",
    "ten_god", "ten_god_distribution", "nayin_of", "judge_match",
    "t", "label", "GLOSSARY",
]
__version__ = "0.1.0"
