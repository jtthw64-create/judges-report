---
title: Codex 작업 지시 — 대시보드 UI (누적, WO 단위로 관리)
type: work-order
from: Claude(커맨더 세션)
to: Codex
created: 2026-07-16
status: DONE
open_items: []
done_items: [WO-001, WO-002, WO-003, WO-004]
---

# 70 · Codex 작업 지시서

> 이 문서는 **커맨더 세션(Claude)**이 발행하고 **Codex**가 수행한다.
> 배경·환경 세팅은 `00_HANDOFF_Codex_대시보드.md`를 먼저 읽을 것.
> 완료 후 이 문서 하단 **수행 보고**에 결과를 append하고 `status: DONE`으로 바꿀 것.
>
> **전달 방식(2026-07-16 갱신)**: 커맨더가 `mcp__codex-mcp__codex` 도구로 이 문서의 특정 WO 항목을 가리켜 직접 호출한다(`sandbox: "danger-full-access"` — 포트 바인딩·git 작업이 막히지 않도록). 이전엔 문서만 발행해두고 Codex가 알아서 찾아 수행하는 방식이었는데, 이제는 커맨더가 MCP로 능동적으로 실행을 트리거한다. WO 항목의 스펙 자체는 이 문서가 여전히 정본이다.

## 역할 분담 (2026-07-16 확정)
| 담당 | 범위 |
|---|---|
| **Claude(커맨더)** | 사용자 요구 수집·계획·분배·점검. 서지 정제(refinement), reclass review. 데이터(`download_queue.csv`, xlsx) 갱신 |
| **Codex** | **대시보드 UI/프런트엔드 수정 전담** (`build_dashboard.py`의 TEMPLATE 부분) |

⚠️ **경계**: Codex는 `worklist/download_queue.csv`의 **데이터 내용**(서지 정보·status 값)을 직접 고치지 않는다. 데이터는 커맨더/정제 파이프라인이 관리한다. Codex는 그 데이터를 **어떻게 보여줄지**만 담당.

---

## WO-001. 확보완료(HELD_ALREADY) 항목 시각적 구분

### 배경
원본 자료 폴더(`../5 Book 3 Judges Resources/` 하위 전체)를 대조한 결과, **다운로드 대장에 올라있지만 이미 확보된 자료 8건**을 확인했다.
커맨더가 `worklist/download_queue.csv`의 해당 행을 이미 갱신해 두었다:
- `status` 컬럼: `QUEUED` → **`HELD_ALREADY`**
- `notes` 컬럼 끝에 `[확보완료: <원본폴더 상대경로>]` 추가

해당 8건 id: `E-01-017`, `E-01-045`, `G-01-001`, `G-01-004`, `G-01-010`, `G-01-013`, `G-01-015`, `G-01-022`

### 요구사항
`build_dashboard.py`만 수정해서 다음을 구현할 것 (HTML 직접 편집 금지, 반드시 스크립트 수정 후 재생성).

1. **데이터 노출**: 현재 `DATA` 딕셔너리에 `status` 필드가 빠져 있다. CSV의 `status`를 읽어 각 행에 포함시킬 것.

2. **행 시각 구분**: `status == "HELD_ALREADY"`인 항목은 목록에서 이미 확보된 자료임이 한눈에 보이게 할 것.
   - 제안: **`확보완료` 배지** 표시 + 행을 흐리게(dim) 처리
   - 기존 "받음 ✔" 체크(사용자가 수동 체크하는 localStorage 값)와는 **다른 개념**이니 시각적으로 구분되게 할 것.
     - `받음` = 사용자가 이번에 직접 받아서 체크한 것
     - `확보완료` = 원본 폴더에 이미 있던 것(대조로 자동 판정)

3. **상단 통계 타일 추가**: `확보완료` 개수 타일을 추가하고, **클릭 시 해당 항목만 필터링**되게 할 것 (기존 타일들과 동일한 클릭 필터 패턴 따를 것 — 이미 `statDefs` 배열 + `filter` 전역변수 구조로 되어 있음).

4. **미수령 계산 보정**: 현재 "미수령" 수치는 `총자료 - 받음`으로 계산된다. **확보완료 항목은 미수령에서 제외**되어야 사용자가 실제로 구해야 할 자료 수를 정확히 볼 수 있다. 계산식을 조정할 것.

5. **접근 링크 처리**: 확보완료 항목은 이제 새로 다운받을 필요가 없으므로, "열기 ↗" 버튼 대신 **원본 폴더 경로를 표시**하는 게 유용하다. 경로는 `notes` 안의 `[확보완료: ...]` 문자열에 들어있다. (파싱해서 쓸지, CSV에 별도 컬럼을 요청할지는 Codex 판단 — 컬럼 추가가 필요하면 커맨더에게 요청할 것. **17컬럼 고정 규칙**이 있으니 임의 추가 금지.)

### 제약
- `worklist/download_queue.csv`의 **컬럼 순서 17개 고정** — 절대 깨지 않을 것.
- 이 CSV는 매일 09:00/14:00 예약작업도 건드린다. 그 시간대 동시 편집 주의(자세한 건 인수인계 문서 6절).
- 로컬 테스트는 반드시 http 서버로 (`file://`는 fetch 차단됨). 방법은 인수인계 문서 3절.
- 완료 후 `python3 build_dashboard.py` 재생성 → 커밋 → push. GitHub Pages 자동 반영.

### 검증 기준
- 대시보드에서 확보완료 8건이 시각적으로 구분되어 보인다.
- 확보완료 타일 클릭 시 그 8건만 필터링된다.
- 미수령 수치가 확보완료분을 제외한 값으로 나온다.
- 기존 기능(카테고리 필터, 우선순위 토글, 재검토 신청, 교수님 코멘트, 백엔드 폴링)이 모두 정상 작동한다.

---

## WO-002. 저자명 컬럼 추가 + 저자명 정렬

### 배경
현재 표에는 저자명이 "자료" 컬럼 안에 제목과 함께 작은 글씨(`.cite`)로 붙어있고, 별도 컬럼도 없고 정렬 기능도 없다. 사용자가 저자명 기준으로 훑어보거나 찾고 싶어함.

### 요구사항
`build_dashboard.py`만 수정(HTML 직접 편집 금지, 재생성으로 반영).

1. **저자 컬럼 신설**: 표에 "저자" 전용 컬럼을 추가한다. 기존 "자료" 컬럼 안의 저자 표시(`.cite`, `${d.au} (${d.yr})`)는 유지해도 되고 정리해도 되는데(중복 표시 여부는 Codex 판단), 최소한 **별도 컬럼으로 저자명이 명확히 노출**돼야 한다.
2. **저자명 클릭 정렬**: 새 "저자" 컬럼 헤더(`<th>`)를 클릭하면 저자명 오름차순/내림차순 토글 정렬이 된다(다시 클릭하면 방향 전환). 현재 기본 정렬은 `priority`→`confidence`→`author` 순(빌드 시점, Python 쪽)인데, 이건 그대로 두고 **런타임에 사용자가 저자명 클릭으로 재정렬**할 수 있게 하는 것.
3. 정렬 상태는 시각적으로 표시할 것(예: 헤더에 ▲▼ 표시).
4. 기존 필터(카테고리/통계타일/검색/재검토/교수님코멘트/백엔드폴링)와 함께 정상 동작해야 한다 — 정렬은 필터링된 결과 위에서 동작.
5. 모바일 반응형 레이아웃(`@media max-width`)도 깨지지 않게 컬럼 폭 조정.

### 제약
- `worklist/download_queue.csv` 데이터 내용은 건드리지 않는다.
- 로컬 테스트는 http 서버로(`00_HANDOFF_Codex_대시보드.md` 3절).
- 완료 후 `python3 build_dashboard.py` 재생성 → 커밋 → push.

### 검증 기준
- 저자 컬럼이 보이고, 클릭 시 오름차순/내림차순 정렬이 실제로 바뀐다.
- 정렬 방향 표시(▲▼)가 클릭할 때마다 토글된다.
- 검색·필터·카테고리 선택과 함께 써도 정렬이 유지/재적용된다.
- 기존 기능(확보완료 배지, 우선순위 토글, 재검토, 교수님 코멘트) 전부 정상.

---

## WO-003. "교수님 코멘트"→"코멘트" 라벨 변경 + "확보불가" 분류 신설

### 배경
1. "교수님 코멘트" 컬럼/영역 명칭이 너무 김/특정적 — "코멘트"로 단순화 요청.
2. 지금 항목 상태는 `받음`(사용자 수령)·`확보완료`(HELD_ALREADY, 원본폴더에 이미 있음) 두 가지뿐인데, **"찾아봤지만 구할 수 없는 자료"를 표시할 방법이 없다.** 사용자가 항목별로 "이건 확보 불가능"이라고 표시할 수 있어야 한다.

### 요구사항
`build_dashboard.py`만 수정(HTML 직접 편집 금지, 재생성으로 반영). 백엔드(Apps Script) 코드 변경은 **불필요** — 이벤트로그 스키마가 `kind` 자유형이라 새 kind를 추가해도 서버 재배포 없이 그대로 저장된다.

1. **라벨 변경**: 표의 "교수님 코멘트" 컬럼 헤더 텍스트를 **"코멘트"**로 바꿀 것. (내부 JS 변수명 `prof`·localStorage 키·백엔드 kind `"prof"`는 그대로 둬도 됨 — 화면 표시 라벨만 변경.) 관련된 다른 화면 텍스트(안내문 footer 등)에 "교수님 코멘트"가 나오면 같이 "코멘트"로 통일.

2. **"확보불가" 분류 신설**:
   - 각 행에 사용자가 클릭으로 켜고 끌 수 있는 **"확보불가"** 표시(버튼 또는 체크박스, 기존 `mbtn` 스타일 패턴 참고)를 추가한다. 위치는 재검토신청/코멘트 패널 근처나 우선순위 컬럼 옆 등 Codex가 UI상 자연스러운 곳으로 판단해서 배치.
   - 상태 저장은 기존 패턴 그대로: 새 로컬 상태 객체(예: `unavailable`) + localStorage 미러링 + 백엔드 이벤트(새 kind, 예: `"unavailable"`, field1="true"/"false")로 폴링 동기화. `loadFromBackend()`의 fold 로직에 이 kind 처리 분기를 추가할 것.
   - **시각적 구분**: `확보완료`(HELD_ALREADY, 원본폴더에 이미 있음)와는 명확히 다른 배지·스타일로 표시할 것 — 서로 다른 개념이니 혼동되면 안 된다. (`확보완료`=이미 갖고 있음, `확보불가`=시도했으나 못 구함)
   - **상단 통계 타일에 "확보불가" 개수 타일 추가**, 클릭 시 해당 항목만 필터링(기존 `statDefs`+`filter` 패턴 동일 적용).
   - **미수령 계산 보정**: 현재 `미수령 = 총자료 - 확보완료 - (확보완료 아닌 받음)`. 여기에 확보불가 항목도 제외할지는 Codex 판단이 아니라 아래 원칙을 따를 것 — **확보불가로 표시된 항목은 미수령에서 제외**한다(사용자가 더 이상 찾을 필요 없는 항목이므로, 확보완료와 동일한 취급). 즉 `미수령 = 총자료 - 확보완료 - 확보불가 - (확보완료·확보불가 아닌 받음)`.
   - 기존 필터(카테고리/재검토/코멘트/백엔드폴링 등)와 함께 정상 동작해야 한다.

### 제약
- `worklist/download_queue.csv` 데이터 내용은 건드리지 않는다.
- 로컬 테스트는 http 서버로(`00_HANDOFF_Codex_대시보드.md` 3절).
- 완료 후 `python3 build_dashboard.py` 재생성 → 커밋 → push.

### 검증 기준
- 컬럼 헤더가 "코멘트"로 표시된다.
- 각 행에서 "확보불가" 토글이 동작하고, `확보완료`와 시각적으로 구분된다.
- 상단 "확보불가" 타일이 개수를 보여주고 클릭 시 필터링된다.
- 미수령 수치가 확보완료+확보불가를 제외한 값으로 정확히 계산된다.
- localStorage 저장 + 백엔드 폴링 동기화(다른 기기/새로고침에도 상태 유지)가 동작한다.
- 기존 기능(확보완료 배지, 우선순위 토글, 재검토, 저자 정렬, 백엔드 폴링) 전부 정상.

---

## WO-004. 재검토/코멘트 textarea 입력 중 내용 유실 버그 (사용자 신고)

### 배경 (버그 리포트)
사용자 신고: "재검토 사유 입력 칸에 입력이 정상적으로 마감되지 않는 현상(중간에 내용 사라짐). 외부에서 작성 후 붙여넣어야 정상 입력 가능."

### 커맨더가 확인한 원인
`setInterval(loadFromBackend, 20000)`이 20초마다 `render()`를 호출한다. `render()`는 `document.getElementById("rows").innerHTML`을 통째로 재생성하는데, 이때:
- 재검토 textarea(`id="rc_${d.id}"`)와 코멘트 textarea(`id="pf_${d.id}"`)는 사용자가 타이핑하는 값이 **JS 상태(`reclass[id].comment` / `prof[id].comment`)에 실시간 반영되지 않는다** — 각각 "신청" 버튼 클릭(`submitReclass`) 또는 `onblur`(`saveProfComment`) 시점에만 `document.getElementById(...).value`를 읽어 상태에 반영.
- 따라서 사용자가 타이핑 중(아직 신청 안 누름/blur 안 됨) 20초 폴링이 돌면 `render()`가 옛 상태(빈 문자열 또는 이전 저장값)로 **해당 textarea DOM 노드를 통째로 교체**해버려 입력 중이던 텍스트와 포커스가 그대로 날아간다.
- 붙여넣기는 순간적으로 끝나서 20초 창을 피하기 쉬우니 증상이 덜 보였을 뿐, 근본 원인은 같다.

### 요구사항
`build_dashboard.py`만 수정. 다음 중 하나(또는 더 나은 방법)로 해결할 것 — **권장은 A안**:

**A안(권장, 근본 해결)**: `render()` 시작 시 현재 포커스된 요소가 `rc_`/`pf_` textarea라면 `{id, value, selectionStart, selectionEnd}`를 저장해두고, rows 재생성 후 **같은 id의 새 textarea에 값·커서 위치·포커스를 복원**할 것. 이렇게 하면 `render()`가 어떤 이유로 호출되든(폴링이든 다른 트리거든) 사용자가 타이핑 중인 내용이 절대 유실되지 않는다.

**B안(차선, 더 간단)**: `loadFromBackend()`에서 `render()` 호출 전에 `document.activeElement`가 `rc_`/`pf_` textarea인지 확인하고, 그렇다면 **상태(`reclass`/`prof`/`got` 등)는 갱신하되 이번 사이클의 `render()` 호출만 건너뛴다**(다음 사용자 액션이나 다음 폴링 때 자연히 반영). B안은 20초 폴링발 유실만 막고, 다른 render() 트리거(같은 세션 내 다른 행 조작 등)로 인한 유실 가능성은 남는다 — 가능하면 A안으로.

### 제약
- `worklist/download_queue.csv` 데이터 내용은 건드리지 않는다.
- 로컬 테스트는 http 서버로.
- 완료 후 `python3 build_dashboard.py` 재생성 → 커밋 → push.

### 검증 기준
- textarea에 포커스를 두고 타이핑 중일 때 20초 이상 대기해도(또는 폴링을 수동 트리거해도) 입력 중이던 텍스트가 사라지지 않는다.
- 커서 위치도 유지된다(이상적으로는 A안 기준).
- 재검토 신청/코멘트 저장(신청 버튼·blur)은 기존처럼 정상 동작한다.
- 기존 기능(확보완료·확보불가·우선순위·저자정렬·카테고리필터·백엔드폴링) 전부 정상.

---

## 수행 보고
> Codex가 완료 후 아래에 append (담당·일시·변경파일·검증결과·특이사항)

- 담당: Codex
- 일시: 2026-07-16 (KST)
- 변경파일: `build_dashboard.py`, `download_dashboard.html`, `index.html`, `70_Codex_UI_요청.md`
- 검증결과: `python3 build_dashboard.py` 재생성 완료(139행). 생성 HTML의 JavaScript 문법 검사 통과. `status=HELD_ALREADY` 8건과 원본 경로 8건이 DATA에 포함되고, 확보완료 배지·dim 행 스타일·타일 필터·경로 대체 렌더링이 생성물에 반영됨을 확인. 초기 `받음` 0건 기준 미수령은 기존 139건에서 확보완료 8건을 제외한 131건으로 보정. 기존 필터·재검토·교수님 코멘트·백엔드 폴링 코드 보존 및 JS 파싱 통과.
- CSV 확인: `worklist/download_queue.csv`는 Git HEAD 대비 diff 0. 헤더 순서와 139개 데이터 행 전체가 17열임을 확인.
- 특이사항: notes 마지막의 `[확보완료: ...]` 패턴을 비탐욕 정규식으로 파싱하되, 패턴이 없는 비정상 `HELD_ALREADY` 행은 `경로 확인 필요`로 보수적 표시. 현재 실행 샌드박스가 로컬 포트 바인딩(`PermissionError: Operation not permitted`)과 in-app Browser 제공을 차단해 HTTP 실브라우저 클릭 검증은 수행할 수 없었음. 대신 생성 HTML 구조·DATA 건수·필터 조건·JS 문법을 정적 검증함. 또한 `.git/index.lock` 생성이 샌드박스 정책으로 차단되어(`Operation not permitted`) 지정 파일의 `git add`·commit·push는 수행하지 못함.

### 커맨더 검증 (2026-07-16, Claude)
Codex 산출물을 실브라우저(로컬 http 서버)로 라이브 검증함:
- 확보완료 타일 8건 표시, 클릭 시 정확히 8건 필터링 확인.
- `tr.held` 행 8개, `.held-badge` "확보완료" 배지 표시 확인.
- 확보완료 행은 "열기" 링크 대신 원본 경로 텍스트 표시 확인 (예: `./2 Micha Danites/Nuri added/Amit-HiddenPolemicConquest-1990.pdf`).
- 미수령 계산식 검증: `총자료 - 확보완료 - (확보완료 아닌 받음)` 정상 동작(백엔드 Sheets에 남아있던 기존 `받음` 이벤트와 겹쳐도 정합성 유지됨을 확인).
- `worklist/download_queue.csv` HEAD 대비 diff 0 재확인.
- Codex가 커밋하지 못한 변경분(`build_dashboard.py`, `download_dashboard.html`, `index.html`, 본 문서)을 커맨더가 대신 커밋·push함.
- **결론: WO-001 전 항목 검증 통과.**

- 담당: Codex
- 일시: 2026-07-17 00:47 KST
- 변경파일: `build_dashboard.py`, `download_dashboard.html`, `index.html`, `70_Codex_UI_요청.md`
- 검증결과: `python3 build_dashboard.py` 재생성 완료(197행). 생성 HTML 2종의 내용 동일성, CSV/DATA 197행 일치, CSV 전 행 17열, 9개 표 컬럼, 저자 전용 컬럼, 필터 → 저자 정렬 → 렌더 순서, 오름차순/내림차순 토글과 ▲/▼·`aria-sort` 상태 표시, 모바일 카드의 저자 라벨을 정적 검증함. 추출 JavaScript에 대해 `node --check` 통과. 확보완료·우선순위 토글·재검토·교수님 코멘트·백엔드 폴링 코드가 유지됨을 확인함.
- CSV 확인: `worklist/download_queue.csv`는 Git HEAD 대비 diff 0이며 수정하지 않았음.
- 특이사항: 샌드박스가 로컬 HTTP 서버의 포트 바인딩을 `PermissionError: [Errno 1] Operation not permitted`로 차단해 실브라우저 클릭 및 화면 폭별 시각 검증은 수행하지 못했음. 따라서 생성 HTML 구조·DATA·CSS·JavaScript 문법과 실행 순서를 정적으로 검증함. `.git/index.lock` 생성도 `Operation not permitted`로 차단되어 지정 파일의 `git add`·commit·push를 수행하지 못했음. 작업 시작 전부터 존재하거나 작업 중 외부 프로세스가 만든 `worklist/UNRESOLVED.csv`, `worklist/C-01a.csv`, `worklist/C-01b.csv`, `worklist/C-01c.csv` 변경은 건드리거나 스테이징하지 않음.

### 커맨더 검증 (2026-07-17, Claude)
Codex 산출물을 실브라우저(로컬 http 서버)로 라이브 검증함:
- "저자" 헤더 클릭 → `aria-sort` `none`→`ascending`, 표시행 순서 실제 변경 확인.
- 재클릭 → `ascending`→`descending`, 헤더 텍스트 "저자 ▼"로 변경, Z→A 역순 정렬 확인.
- 정렬 활성 상태에서 카테고리 필터 클릭 → 필터링된 58건 내에서도 정렬 순서 유지됨 확인.
- `worklist/download_queue.csv` HEAD 대비 diff 0 재확인.
- Codex가 커밋 못 한 변경분(`build_dashboard.py`, `download_dashboard.html`, `index.html`, 본 문서)을 커맨더가 대신 커밋·push함.
- **결론: WO-002 전 항목 검증 통과.**

- 담당: Codex
- 일시: 2026-07-17 (KST)
- 변경파일: `build_dashboard.py`, `download_dashboard.html`, `index.html`, `70_Codex_UI_요청.md`
- 검증결과: `python3 build_dashboard.py` 재생성 완료(1,051행). 생성 HTML 2종의 내용 동일성, CSV/DATA 1,051행 일치, CSV 전 행 17열, 표·모바일·footer의 “코멘트” 라벨, 확보불가 토글·로컬저장·`unavailable` 백엔드 이벤트(field1=true/false)·폴링 fold·배지/행 스타일·통계 타일 필터·미수령 제외식을 정적 검증함. 추출 JavaScript의 `node --check` 통과, `git diff --check` 통과. 기존 확보완료·저자 정렬·우선순위·재검토·코멘트·백엔드 폴링 코드가 유지됨을 확인함.
- CSV 확인: `worklist/download_queue.csv`는 Git HEAD 대비 diff 0이며 수정하지 않음.
- 특이사항: 샌드박스가 `git pull` 시 `.git/FETCH_HEAD` 쓰기를 `Operation not permitted`로 차단해 원격 동기화를 수행하지 못함. 로컬 HTTP 서버도 `PermissionError: [Errno 1] Operation not permitted`로 포트 바인딩이 차단되어 실브라우저 클릭 검증은 수행하지 못했고, 생성 HTML 구조·DATA·CSS·JS 문법과 상태 조건을 정적 검증함. `git add` 시 `.git/index.lock` 생성도 `Operation not permitted`로 차단되어 commit·push는 수행하지 못함. WO-003 지시에 따라 Apps Script 코드는 변경하지 않음.

### 커맨더 검증 및 백엔드 버그 수정 (2026-07-17, Claude)
Codex 산출물을 실브라우저(로컬 http 서버)로 라이브 검증하는 과정에서 **백엔드 미대응 버그를 발견**했다:
- WO-003 지시서에 "새 kind는 서버 재배포 없이 자유형으로 저장된다"고 잘못 적었음 — **사실이 아니었다.** 실제 Apps Script `doPost`는 `kind`별 `if/else if` 하드코딩 스위치라, 목록에 없는 `"unavailable"` kind는 `field1/2/3`이 전부 빈 문자열로 저장됨(백엔드 Sheets에서 `field1: ''` 확인).
- `worklist/apps_script_backend.gs`에 `else if (kind === "unavailable") { f1 = data.field1 || ""; }` 분기 추가, Apps Script 프로젝트에 새 버전(버전 3)으로 재배포(exec URL은 그대로 유지됨).
- 재배포 후 curl로 POST→GET 왕복 재확인: `field1` 정상 저장(`true`/`false`) 확인.
- 실브라우저 전체 흐름 재검증: 토글 클릭 → `unavailable[id]=true` → 1.5초(백엔드 폴링 유예) 후에도 상태 유지 → `tr` 클래스에 `unavailable` 추가, `.unavailable-badge` "확보불가" 표시, 통계 타일 0→1 반영 확인. 재클릭으로 원복도 정상.
- 테스트 중 생성된 시트 이벤트(G-01-001/I-01-001/TEST-002)는 정리하거나 최종 상태가 기본값(false)으로 수렴함을 확인.
- `worklist/download_queue.csv` HEAD 대비 diff 0 재확인.
- Codex가 커밋하지 못한 변경분(`build_dashboard.py`, `download_dashboard.html`, `index.html`, `worklist/apps_script_backend.gs`, 본 문서)을 커맨더가 대신 커밋·push함.
- **결론: WO-003 전 항목 검증 통과(백엔드 수정 포함).** 향후 새 이벤트 kind를 추가할 때는 **반드시 Apps Script `doPost`에도 분기를 추가**해야 한다는 점을 인수인계 문서에 반영 필요(자유형이 아님).

- 담당: Codex
- 일시: 2026-07-18 03:59 KST
- 변경파일: `build_dashboard.py`, `download_dashboard.html`, `index.html`, `70_Codex_UI_요청.md`
- 검증결과: WO-004 A안을 적용해 `render()` 시작 시 포커스된 `rc_`/`pf_` textarea의 id·입력값·선택 시작/끝을 캡처하고, 행 DOM 재생성 직후 같은 textarea에 값·포커스·커서(선택 범위)를 복원하도록 구현함. `python3 build_dashboard.py` 재생성 완료(1,051행), 생성 HTML 2종 내용 동일성 및 복원 로직 포함 여부 확인, 추출 JavaScript `node --check` 통과, `git diff --check` 통과. DOM 모의 실행으로 입력값·포커스·선택 범위 복원과 비대상 input 무시를 확인함. 기존 신청 버튼/blur 저장 및 백엔드 폴링 로직은 변경하지 않음.
- CSV 확인: `worklist/download_queue.csv`는 Git HEAD 대비 diff 0이며 수정하지 않음.
- 특이사항: 샌드박스가 로컬 HTTP 서버 포트 바인딩을 `PermissionError: [Errno 1] Operation not permitted`로 차단해 20초 폴링을 포함한 실브라우저 검증은 수행하지 못함. 생성물 문법·호출 순서·DOM 모의 테스트로 대체 검증함.
