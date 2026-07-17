---
title: 인수인계 — 대시보드 작업을 Codex로 이전
type: handoff
from: Claude Code
to: Codex
updated: 2026-07-15
---

# 00-C · Claude → Codex 인수인계 (대시보드 작업)

> **이 문서의 성격이 2026-07-17에 바뀌었다.** 원래는 "Claude Code 토큰 한도로 대시보드 작업 전체를 Codex가 이어받는" 완전 인수인계 시나리오용이었다. 지금은 **커맨더 세션(`00_COMMANDER.md`)이 살아있고, 평상시엔 `mcp__codex-mcp__codex`로 Codex를 직접 호출**해 작업을 배분한다(`00_COMMANDER.md` 2절 참고). 이 문서는 그 MCP 호출 안에서 Codex가 참고할 환경설명 자료로도 쓰이고, **커맨더 세션 자체가 끊겨서 Codex가 완전히 단독으로 이어받아야 하는 비상 상황**을 위한 완전 인수인계본으로도 남겨둔다. 두 경우 다 아래 내용은 유효하다.
>
> ⚠️ 이 폴더에 `2026-07-15_Codex_인수점검_보고서.md`라는 파일도 있는데, 그건 오래된 스냅샷 기준이라 낡았다(카테고리 필터·Major/Secondary 배지·백엔드 연동·확보완료 표시 등 최근 기능이 반영 안 됨). 이 문서(`00_HANDOFF_Codex_대시보드.md`)가 최신 정본이다.

## 0. 시작 전 필수
```
cd "judges report/"
git pull   # 로컬 HEAD가 origin보다 뒤처져 있을 수 있으니 반드시 먼저 pull
git log --oneline -12   # 최근 커밋으로 최신 상태 확인
```

## 1. 프로젝트 구조
- 대상 폴더: `judges report/` (git 저장소, 이 문서가 있는 폴더)
- 원본 서지(읽기전용, 절대 쓰기 금지): `../5 Book 3 Judges Resources/judges-index/` 및 `judges-index/extracted/`
- 정본 데이터: `worklist/download_queue.csv` (17컬럼 고정: id,source_track,category,author,year,title,journal_series,boundary,priority,confidence,access_link,xlsx_ref,id_type,identifier,cited_by,status,notes)
- 대시보드 생성기: `build_dashboard.py` — `worklist/download_queue.csv`를 읽어 `download_dashboard.html`과 `index.html`(GitHub Pages 진입점, 내용 동일)을 생성. **HTML을 직접 손대지 말고 항상 `build_dashboard.py`를 고친 뒤 재생성할 것.**
- 대시보드 변경요청 접수 관행: `60_대시보드_변경요청.md` — 사용자가 요청을 순차로 올리면 접수만 해두고, "완료, 실행"이라 말할 때 일괄 처리하는 방식으로 운영해왔다. Codex도 같은 패턴을 쓰면 사용자가 편하다(강제 아님).

## 2. GitHub
- Repo: `https://github.com/jtthw64-create/judges-report` — **public**
- 로컬 remote: SSH — `git@github.com:jtthw64-create/judges-report.git`
- 이 Mac(nurisimac)에 SSH 키 등록·인증 완료됨(`~/.ssh/id_ed25519`, GitHub에 이미 공개키 등록됨). `git push`/`pull` 별도 인증 없이 됨.
- git 커밋 시 "Committer 이름/이메일 자동감지" 경고가 뜨는데(`nurikim@nurisimac.local`) 무시해도 됨(차단 아님).
- **정책**: 원본 서지(`5 Book 3 Judges Resources/`)는 git에 절대 포함 금지. `judges report/` 산출물만 public repo에 올라간다(현재도 그렇게 되어 있음).

### GitHub Pages
- URL: **https://jtthw64-create.github.io/judges-report/**
- 설정: repo Settings → Pages → Source = `main` 브랜치, `/` (root). 이미 켜져 있음, 추가 조작 불필요.
- `index.html`을 커밋+push하면 보통 30초~1분 내 자동 재배포됨. 배포 완료 확인 팁:
  ```
  until curl -s "https://jtthw64-create.github.io/judges-report/" | grep -q "<특징적인 문자열>"; do sleep 3; done
  ```

## 3. 로컬에서 대시보드 테스트하는 법 (중요)
`index.html`을 `file://`로 그냥 열면 **fetch가 차단되어 백엔드 연동이 작동하지 않는다**(Codex의 이전 점검 보고서에도 이 문제가 기록돼 있음). 반드시 로컬 HTTP 서버로 서빙해서 테스트할 것:
```
cd "judges report/"
lsof -ti:8934 | xargs -r kill -9   # 이전에 띄워둔 서버 정리
python3 -m http.server 8934 &
# 브라우저에서 http://localhost:8934/index.html 로 접속
```
JS 문법만 빠르게 검사하려면:
```
python3 -c "
import re
html = open('index.html', encoding='utf-8').read()
m = re.search(r'<script>(.*)</script>', html, re.S)
open('/tmp/dash.js','w',encoding='utf-8').write(m.group(1))
"
node --check /tmp/dash.js && echo OK
```

## 4. 백엔드 — Google Sheets + Apps Script Web App
정적 GitHub Pages는 서버가 없어서, 사용자 입력(재검토 코멘트/교수님 코멘트/우선순위 변경)을 저장하려고 별도 백엔드를 만들어 붙여놨다.

- Google Sheet: 이름 "제목 없는 스프레드시트"(리네임 시도했으나 UI 자동화로 실패, 기능엔 무관 — 원하면 고쳐도 됨)
  - Spreadsheet ID: `1EZu2htHichsGf30ujWeM0-nd5zA_tfAHJH0hl9nmeJo`
  - 링크: `https://docs.google.com/spreadsheets/d/1EZu2htHichsGf30ujWeM0-nd5zA_tfAHJH0hl9nmeJo/edit`
  - 시트 탭 "events" 하나만 사용. 헤더: `ts, kind, id, field1, field2, field3`
  - **이벤트로그 방식(append-only)**: 모든 변경이 새 행으로 쌓임. 같은 id에 대해 여러 행이 있으면 **가장 최근(ts) 행이 현재 상태**. GET 응답을 그대로 시간순 fold해서 상태를 복원한다(대시보드 JS의 `loadFromBackend()` 참고).
  - ⚠️ **kind는 자유형이 아니다.** Apps Script `doPost`가 `kind`별 `if/else if` 하드코딩 스위치로 `field1/2/3`을 채운다. **새 kind를 클라이언트(build_dashboard.py)에 추가할 때마다 `worklist/apps_script_backend.gs`의 `doPost`에도 분기를 추가하고 재배포해야 한다** — 안 하면 그 kind는 `field1/2/3`이 전부 빈 문자열로 저장된다(WO-003에서 `unavailable` kind 추가 시 이걸 빠뜨려서 실제로 겪었다. 커맨더가 사후 발견·수정·재배포함).
  - kind별 필드 의미(현재 doPost가 처리하는 것):
    - `got`: field1 = "true"/"false" (받음 체크)
    - `priority_change`: field1=이전 boundary값, field2=새 값(또는 `"__revert_to_original__"`=복원), field3=review 상태
    - `reclass`: field1=사용자 코멘트, field2=status("pending"/"ai_reviewed"), field3=AI 검토결과 텍스트
    - `prof`: field1=choice("prio"/"skip"/""), field2=코멘트
    - `unavailable`: field1 = "true"/"false" (확보불가 표시, WO-003)

- Apps Script 프로젝트(이 Sheet에 바인딩됨):
  - 프로젝트 URL: `https://script.google.com/u/0/home/projects/1K8qQFCWPxUjVkE9b-R0DJojFIvYuW3ci_2kh4Kor7Gk5wcpOr7mr3doa/edit`
  - 소스 코드 로컬 사본(참고용, git 추적됨): `worklist/apps_script_backend.gs` — **Apps Script는 git/CLI로 직접 배포 안 됨(clasp 미설치). 코드를 고치면 반드시 (a) 이 로컬 .gs 파일도 같이 고치고 (b) 아래 배포 절차로 실제 배포판도 갱신할 것. 둘이 안 맞으면 다음 사람이 헷갈린다.**
  - 배포된 Web App URL(GET=조회, POST=기록):
    ```
    <WEB_APP_URL — build_dashboard.py의 SHEETS_ENDPOINT 상수에 실값 있음>
    ```
  - 배포 설정: 실행 계정 = 소유자, 액세스 범위 = 링크를 아는 사용자. 실제 URL 값은 `build_dashboard.py`의 `SHEETS_ENDPOINT` 상수에 있으니 필요할 때 거기서 확인할 것(문서에는 값 미기재). 이 저장소가 public이라 URL이 소스에 노출되는 구조이며, 사용자가 이 점을 인지하고 현행 구성으로 진행하기로 결정한 상태다. 접근 제어 방식을 바꾸려면 사용자와 먼저 상의할 것.

### Apps Script 코드 수정 → 재배포 절차 (실제로 해본 순서)
1. 프로젝트 URL 접속 → `Code.gs` 편집 → 저장(Cmd+S).
   - **주의**: 에디터가 자동 들여쓰기를 하므로 붙여넣기 후 들여쓰기가 밀릴 수 있다. JS는 들여쓰기 무관하니 기능엔 문제없지만, 안 보기 불편하면 손으로 정리.
2. 상단 "배포" 드롭다운 → "배포 관리".
3. 연필(수정) 아이콘 클릭.
4. "버전" 드롭다운 → **"새 버전"** 선택 (기존 버전 번호 그대로 두면 코드 반영 안 됨).
5. "배포" 버튼 클릭 → 완료. **URL은 그대로 유지된다** (버전만 올라감, exec URL 안 바뀜).
6. 최초 배포 시에는 "액세스 승인" 팝업이 뜰 수 있다(자기 자신 계정에 대한 권한 부여라 위험한 동작 아님). 팝업이 새 창으로 안 뜨고 응답이 없으면, 대신 편집기 상단 "실행" 버튼으로 아무 함수나 한 번 실행해서 인라인 "권한 검토" 대화상자로 승인을 처리하면 된다(실제로 겪었던 이슈, 이 방법으로 해결됨).
7. curl로 검증:
   ```
   curl -sL "<WEB_APP_URL — build_dashboard.py의 SHEETS_ENDPOINT 상수에 실값 있음>"
   # {"ok":true,"rows":[...]}
   ```
   POST 테스트:
   ```
   curl -sL "<위 URL>" -X POST -H "Content-Type: text/plain" -d '{"kind":"got","id":"TEST","got":true}'
   ```
   (POST 응답 자체가 이상한 HTML 에러 페이지로 보일 때가 있었는데, 실제로는 정상 기록됨 — 반드시 GET으로 재확인할 것. **테스트 후에는 시트에서 테스트 행을 지울 것** — 이벤트로그라 안 지우면 계속 남아서 프런트 통계가 오염됨.)

## 5. 대시보드 프런트엔드 구조 (`build_dashboard.py` 안의 TEMPLATE)
- `DATA` 배열: CSV 각 행 → `{id, pri, bd, cat, conf, au, yr, ti, js, link, ref, warn, info}`.
- 표시 라벨 매핑: `LBL = {통독:'Major', 표적:'Secondary', 'off-list':'Off-list'}` — **CSV 원값은 그대로 통독/표적/off-list 유지**하고 화면에서만 영문 라벨로 바꿔치기 하는 방식(데이터 자체는 안 바꿈).
- 로컬 상태(모두 localStorage에도 미러링): `got`(받음 체크), `bdOverride`(우선순위/바운더리 토글값), `bdHistory`(변경이력, 복원용), `reclass`(재검토 신청), `prof`(교수님 코멘트).
- `loadFromBackend()`: 페이지 로드 시 1회 + `SHEETS_ENDPOINT`가 설정돼 있으면 20초마다 폴링, 백엔드 이벤트를 fold해서 로컬 상태에 병합 → `render()`.
- `render()`: 상단 통계 타일(총자료/받음/미수령/Major/C확인요/재검토대기/교수님미확인/표시중) — **전부 클릭 가능**하고 클릭한 타일은 파란 테두리로 활성 표시됨. 카테고리 타일도 클릭 필터. `filter` 전역 변수 `{type, value?}`로 현재 필터 상태 관리.
- 표 컬럼: 받음 / 우선(클릭:전환, boundary 3단계 순환) / 자료 / 저널·시리즈 / 접근 / 원본엑셀위치 / 재검토신청(코멘트박스) / 교수님코멘트(우선받기·불필요 버튼+코멘트박스+확인함체크).

## 6. Claude Code 예약 작업 (Codex가 못 보고 못 건드리는 것 — 알고만 있을 것)
이 Mac의 Claude Code 앱에 두 개의 **일일 자동 스케줄**이 등록돼 있다. Codex는 이 스케줄을 조회·수정·중지할 수 없다(Claude Code 전용 기능, 파일 경로만 존재: `~/.claude/scheduled-tasks/<id>/SKILL.md`). 계속 백그라운드에서 돌아가니 **동시 편집 충돌**을 피하려면 아래 시간대에 같은 파일을 만지지 않는 게 안전하다.

| 작업 | 시각(KST) | 하는 일 | 건드리는 파일 |
|---|---|---|---|
| `judges-report-daily-refinement` | 매일 14:00 | 서지 정제 배치(청크 3개) 진행 여부를 사용자에게 물어보고, 승인 시 `worklist/download_queue.csv`·`20_PROGRESS_TRACKER.md`·`worklist/refinement_queue.md` 갱신 후 대시보드 재생성·git push | `download_queue.csv`, `20_PROGRESS_TRACKER.md`, `worklist/refinement_queue.md`, `index.html`, `download_dashboard.html`, `50_정제_이벤트로그.md` |
| `judges-report-reclass-review` | 매일 09:00 | 대시보드에서 접수된 "재검토 신청" pending 건을 원본 서지와 대조해 AI가 판정, Sheets 백엔드에 결과 기록, 필요시 `download_queue.csv` 정정 | `download_queue.csv`(정정 시), Sheets `events` (POST) |

이 두 작업은 사용자가 대시보드에서 지금까지 요청한 "이벤트로그 + 하루 1회 지정시간 처리" 요구사항 구현물이다. **Codex가 대시보드 기능을 더 추가할 때 이 스케줄들이 기대하는 CSV 컬럼 순서(17개 고정)·Sheets 이벤트 스키마(kind/field1/2/3)를 깨지 않도록 주의.** 스키마를 바꿔야 한다면 위 두 SKILL.md 프롬프트도 함께 고쳐야 하므로 사용자에게 알릴 것(Codex가 직접 파일을 고칠 수는 있음 — 그냥 텍스트 파일이라 — 다만 그 안의 지시문 내용을 잘 이해하고 고칠 것).

## 7. 지금까지 완료된 대시보드 기능 (변경 이력 요약)
`60_대시보드_변경요청.md`에 상세 기록 있음. 요약:
1. 통독→Major, 표적→Secondary 표시명 변경(데이터값은 유지, 화면 매핑만)
2. 재검토 신청 UI(코멘트박스) + 매일 09:00 AI 검토 파이프라인
3. 교수님 코멘트 칸(우선받기/불필요 버튼 + 코멘트, AI 자동처리 대상 아님, "확인함" 체크로 알림 해제)
4. 우선순위(boundary) 배지 클릭 3단 순환 토글(Major↔Secondary↔Off-list) + 복원 버튼 + 변경이력
5. 카테고리 타일 클릭 필터, 상단 통계 타일 전부 클릭 가능(총자료/받음/미수령/Major/C확인요/재검토대기/교수님미확인)

## 8. 알려진 한계 / 다음에 고려할 것 (강제 아님, 참고용)
- 교수님 Google 계정과 시트 공유가 아직 안 돼 있음(사용자가 "지금은 나만 구축, 이후 공유 조정" 결정). 공유하려면 시트 우측 상단 "공유"에서 교수님 이메일 추가.
- events 시트가 append-only라 계속 커진다. 압축/정리 로직 없음 — 필요해지면 만들 것.
- Apps Script 엔드포인트는 현재 링크 기반 접근이라 접근 제어가 느슨함(사용자가 인지하고 현행 유지 중). 강화 필요 시 사용자와 상의.
- 스프레드시트 제목이 "제목 없는 스프레드시트"로 남아있음(리네임 실패, 기능엔 무해).
