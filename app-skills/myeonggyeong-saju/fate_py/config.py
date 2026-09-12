"""전역 진태양시 설정 — fate-js src/config.ts 1:1 미러링.

env: BAZI_SOLAR_TIME(=1/0) · BAZI_LONGITUDE · BAZI_STD_MERIDIAN · BAZI_EOT(=1/0)
code: set_solar_config({...}) / get_solar_config()
"""

import os

from .validate import assert_longitude


def _env(name: str):
    return os.environ.get(name)


def _env_num(name: str, dflt: float) -> float:
    v = _env(name)
    if v is None:
        return dflt
    try:
        n = float(v)
    except (TypeError, ValueError):
        return dflt
    return n if _is_finite(n) else dflt


def _is_finite(n: float) -> bool:
    return n == n and n not in (float("inf"), float("-inf"))


def _env_bool(name: str, dflt: bool) -> bool:
    v = _env(name)
    if v is None:
        return dflt
    return v == "1" or v.lower() == "true"


_cfg = {
    "applySolarTime": _env_bool("BAZI_SOLAR_TIME", True),
    "applyEot": _env_bool("BAZI_EOT", True),
    "standardMeridian": _env_num("BAZI_STD_MERIDIAN", 135),
    "defaultLongitude": _env_num("BAZI_LONGITUDE", 127.5),
}


def get_solar_config() -> dict:
    return dict(_cfg)


def set_solar_config(patch: dict) -> None:
    """부분 갱신. undefined(None) 키는 무시. 비유한 경도·자오선은 거부."""
    global _cfg
    clean = {}
    if patch.get("applySolarTime") is not None:
        if not isinstance(patch["applySolarTime"], bool):
            raise TypeError(f"applySolarTime는 boolean이어야 합니다: {patch['applySolarTime']!r}")
        clean["applySolarTime"] = patch["applySolarTime"]
    if patch.get("applyEot") is not None:
        if not isinstance(patch["applyEot"], bool):
            raise TypeError(f"applyEot는 boolean이어야 합니다: {patch['applyEot']!r}")
        clean["applyEot"] = patch["applyEot"]
    if patch.get("standardMeridian") is not None:
        assert_longitude(patch["standardMeridian"], "standardMeridian")
        clean["standardMeridian"] = patch["standardMeridian"]
    if patch.get("defaultLongitude") is not None:
        assert_longitude(patch["defaultLongitude"], "defaultLongitude")
        clean["defaultLongitude"] = patch["defaultLongitude"]
    _cfg = {**_cfg, **clean}
