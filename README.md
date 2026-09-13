<!--
  이 파일은 사람도 읽지만, AI가 읽고 "지금 사용자가 있는 플랫폼"에 맞게
  스스로 설치·실행하도록 라우팅하는 안내서이기도 하다.
-->

# 명경(明鏡)

**운명을 비추는 거울.** 사주·궁합을 있는 그대로 — 풀이마다 근거를 함께 보여줍니다.

- **계산은 검증된 엔진이, 해석은 AI가.** 사주는 지어내지 않습니다.
- **겁주지 않아요.** 불리한 배치도 담담히, "어떻게 다루는지"까지.
- **점수(%)를 매기지 않아요.** 궁합은 몇 점이 아니라 "어디서 끌리고 어디서 부딪히는지".

랜딩: <https://greyfolk99.github.io/myeonggyeong/>

---

## AI에게 — 자동 설치·라우팅

> 사용자가 "이 저장소(github.com/greyfolk99/myeonggyeong)를 참조해서 명경을 설치해줘"라고 하면,
> 아래 순서로 **지금 사용자의 환경을 판단**해 알맞은 방법을 골라 진행하세요.

1. **터미널 + git 이 있는 환경** (Claude Code · Codex · Cursor · 로컬 개발)
   → 아래 [플랫폼별 설치](#플랫폼별-설치)의 해당 항목을 쓰거나, 저장소를 clone 해 **코어 스킬**을 실행.
2. **웹/앱 챗인데 파이썬 코드 실행이 되는 환경** (ChatGPT 데이터분석 · Claude 앱 코드실행)
   → 저장소의 raw 파일을 받아 샌드박스에 저장하고 **코어 스킬**을 실행. (외부 라이브러리 불필요)
3. **개인 Skill 업로드를 지원하는 앱**
   → `app-skills/myeonggyeong-saju` 폴더(또는 [ZIP](assets/myeonggyeong-saju.zip))를 업로드.
4. **코드 실행이 전혀 안 되는 순수 챗봇**
   → 사주를 지어내지 말고, 위 1~3 환경 중 하나에서 열어달라고 안내.

**공통 규칙(반드시 준수):** 계산은 엔진(`bin/*.py`)이 하고, 해석은 각 스킬 폴더의
`SKILL.md` 와 `reference/interpretation-guide.md` 를 그대로 따릅니다. 없는 항목을 있다고 하지 않습니다.

---

## 코어 스킬 (모든 환경 공통 · 순수 파이썬)

외부 라이브러리 없이 **표준 파이썬만으로** 도는 자립형 사주 엔진(fate_py)이 통째로 들어 있습니다.

| 무엇 | 폴더 | 실행 |
|---|---|---|
| 나의 사주 (한 사람) | `app-skills/myeonggyeong-saju` | `python bin/saju.py --year 1992 --month 8 --day 4 --hour 3 --minute 30 --gender female` |
| 연애 궁합 (두 사람) | `app-skills/myeonggyeong-gunghap` | `python bin/gunghap.py --a-year … --a-gender female --b-year … --b-gender male` |

- 시간을 모르면 `--hour`/`--minute` 를 빼세요(시주 기반 항목은 계산하지 않습니다).
- 출력은 **사람이 읽는 요약** + `===JSON===` 뒤의 **팩트(JSON)** — 해석은 이 JSON을 근거로 삼습니다.
- 자세한 사용법·해석 규칙은 각 폴더의 `SKILL.md`.

```bash
# 예: 저장소를 받아 바로 실행
git clone https://github.com/greyfolk99/myeonggyeong
cd myeonggyeong/app-skills/myeonggyeong-saju
python bin/saju.py --year 1992 --month 8 --day 4 --hour 3 --minute 30 --gender female
```

---

## 플랫폼별 설치

### Claude Code (TUI)
Claude Code 화면 안에 입력:
```
/plugin marketplace add greyfolk99/myeonggyeong
/plugin install myeonggyeong@myeonggyeong
```

### Codex (CLI)
터미널(쉘)에서:
```
codex plugin marketplace add greyfolk99/myeonggyeong
codex plugin add myeonggyeong@myeonggyeong
```

### ChatGPT · Claude 앱 (웹·데스크탑)
파이썬 코드 실행이 켜져 있으면 코어 스킬이 그대로 돕니다. 이렇게 붙여넣으세요:
```
github.com/greyfolk99/myeonggyeong 의 app-skills/myeonggyeong-saju 를 받아
python bin/saju.py 로 내 사주를 계산하고, 그 폴더의 SKILL.md·reference/interpretation-guide.md
규칙대로 해석해줘. 내 정보: 생년월일(양력)·태어난 시각·성별 → [여기에 입력]
```
개인 Skills 업로드를 지원하면 `app-skills/myeonggyeong-saju` 폴더(또는 [ZIP](assets/myeonggyeong-saju.zip))를 업로드해도 됩니다.

### 그 밖의 AI (Cursor · Gemini 등)
저장소를 clone 하거나 raw 파일을 읽어 `app-skills/*/bin/*.py` 를 실행하고, 결과를 해당 폴더의 가이드대로 해석.

---

## 원칙 요약
- 계산은 엔진이, 해석은 AI가 — **사주를 지어내지 않는다.**
- **겁주지 않기 · 점수(%) 없음 · 근거는 각주 · 한자엔 한글 병기.**
- 관상(얼굴)은 준비 중.

*엔진(fate_py)은 fate-js(사주 계산 엔진)의 순수 파이썬 1:1 포팅본으로, 동일 입력 20,000+건 대조로 결과 일치를 검증했습니다.*
