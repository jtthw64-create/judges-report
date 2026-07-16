---
title: 진행 상태 추적기 (세션마다 갱신)
type: tracker
updated: 2026-07-13
---

# 20 · PROGRESS TRACKER

새 세션은 여기서 **다음 배치/청크**를 확인하고, 작업 후 **세션 로그를 append**한다.

## 상태 코드
`NEW` 미착수 · `IN_PROGRESS` 진행중 · `DONE` 정제+식별+중복재확인 완료 ·
`PARTIAL` 일부만 · (항목 status는 청크 CSV 내부에 기록)

## 배치·청크 현황 (진행 순서 = 가벼운 것부터)
| 진행# | 청크 | 카테고리 | 건수 | 상태 | 완료일 | 산출물 |
|---|---|---|---|---|---|---|
| 1 | K-01 | Tola·Jair | 1 | DONE | 2026-07-13 | worklist/K-01.csv |
| 2 | J-01 | Shamgar | 5 | DONE | 2026-07-13 | worklist/J-01.csv |
| 3 | I-01 | Ehud | 6 | DONE | 2026-07-13 | worklist/I-01.csv |
| 4 | H-01 | Gibeah·Concubine | 17 | DONE | 2026-07-13 | worklist/H-01.csv |
| 5 | G-01 | Micah·Danites | 24 | DONE | 2026-07-13 | worklist/G-01.csv |
| 6 | F-01 | Jephthah | 35 | DONE | 2026-07-14 | worklist/F-01.csv |
| 7 | E-01 | Gideon·Abimelech | 61 | DONE | 2026-07-14 | worklist/E-01.csv |
| 8 | D-01 | Deborah·Jael·Barak | 62 | DONE | 2026-07-17 | worklist/D-01.csv |
| 9 | C-01 | Samson | 133 | DONE | 2026-07-17 | worklist/C-01.csv (a/b/c 3분할 병합) |
| 10 | B-01 | Book·Composition | ~110 | NEW | | |
| 10 | B-02 | Book·Composition | ~110 | NEW | | |
| 10 | B-03 | Book·Composition | ~102 | NEW | | |
| 11 | A-01 | General·ANE | ~150 | NEW | | |
| 11 | A-02 | General·ANE | ~150 | NEW | | |
| 11 | A-03 | General·ANE | ~150 | NEW | | |
| 11 | A-04 | General·ANE | ~150 | NEW | | |
| 11 | A-05 | General·ANE | ~150 | NEW | | |
| 11 | A-06 | General·ANE | ~150 | NEW | | |
| 11 | A-07 | General·ANE | ~150 | NEW | | |
| 11 | A-08 | General·ANE | ~150 | NEW | | |
| 11 | A-09 | General·ANE | ~150 | NEW | | |
| 11 | A-10 | General·ANE | ~150 | NEW | | |
| 11 | A-11 | General·ANE | ~150 | NEW | | |
| 11 | A-12 | General·ANE | ~79 | NEW | | |

**집계:** 완료 9 / 23청크 · 처리(원행) 344 / 2395건 · download_queue **320항목**(HELD_ALREADY 30 포함) · UNRESOLVED 8

## 다음 액션
→ **B-01 (Book·Composition, ~110건)** 정제. (`40_검증방법론.md` 절차 준수, Sonnet 서브에이전트 위임 — 대형 배치이므로 분할 위임 권장)
- download_queue.csv 컬럼(17, 순서 고정): id,source_track,category,author,year,title,journal_series,boundary,priority,confidence,access_link,xlsx_ref,id_type,identifier,cited_by,status,notes
- **status 값은 반드시 `QUEUED` 또는 `HELD_ALREADY`만 사용**(`RESOLVED` 금지 — C-01에서 일부 서브에이전트가 잘못 써서 사후 정정한 사례 있음). UNRESOLVED 항목은 `worklist/UNRESOLVED.csv`에만 넣고 본 청크 CSV에는 넣지 않는다(중복 금지).
- 콤마 포함 필드는 반드시 큰따옴표. append 후 `python3 build_dashboard.py`.
- GitHub repo 연결됨: https://github.com/jtthw64-create/judges-report (public). 매 배치 후 커밋+push.
- 신규 청크마다 `40_검증방법론.md` 8절(원본폴더 확보완료 대조) 재실행 필수. **`download_queue.csv` 전체 갱신 후 `python3 worklist/held_audit.py`로 재점검**(8-5절 원칙).

---

## 세션 로그 (최신이 위로 append)

### 2026-07-17 · 세션 9 (C-01 3분할 병렬 + 확보완료 재점검 11건 추가)
- **C-01 (Samson, 133행) DONE** — 3분할(C-01a/b/c) 병렬 Sonnet 위임. 133→**123 확정 고유**(HELD_ALREADY 8, QUEUED 115) + **UNRESOLVED 7건**(bömer/Ebeling/Fakasiieiki/Gtu·Gese/Hennann/Lesley/Mazar 2023 — 게재지·소속 미확인).
- 등급 A82/B36/C5.
- ★데이터 정합성 정정: 일부 서브에이전트가 `status=RESOLVED`(관례 위반, 정정: `QUEUED`)와 UNRESOLVED 행 중복 기재(제거, UNRESOLVED.csv에만 유지) — 커맨더가 통합 시 발견·정정.
- ★고위험 저자정정: Sasson, Jack M. 본인 자기인용 2건(C-01a "Chambon"→Sasson), van der Toorn 1건("Bachmann"→van der Toorn), Zakovitch("Younger"→Zakovitch) 등.
- **확보완료 재점검(사용자 지적)**: `worklist/held_audit.py`(제목토큰겹침) 전체 재실행 → **기존 정제분(K~E)에서 11건 추가 발견**(HELD_ALREADY 절차 신설 이전 정제라 누락돼 있었음). 40_검증방법론.md 8-5절 기록.
- 총 **320항목** (9/23 청크, HELD_ALREADY 30). 대시보드 자동빌드 정상.
- Codex WO-002(저자 컬럼+정렬) 완료 — MCP 직접호출(`workspace-write` 샌드박스)로 트리거, 커맨더 실브라우저 검증 후 push.
- 다음: B-01 (Book·Composition, ~110건)

### 2026-07-17 · 세션 8 (D-01 + 커맨더 체계 + Codex MCP 연동)
- **D-01 (Deborah·Jael·Barak, 62행) DONE** — Sonnet 서브에이전트 위임. 62→**58 고유**(병합 4쌍).
- 등급 A44/B10/C4, UNRESOLVED 0. **HELD_ALREADY 3건**(Asen 1997·Globe 1974·Margalit 1995 — 원본폴더 "2 Deborah and Jael" 폴더에서 파일 실재 확인).
- ★저자정정 다수(OCR): Artzy→Asen, Burke→Burnette-Bletsch, Latvus→Layton, Lnin→Levin, Marello→Margalit, McCarthy→McDaniel, Schorn→Schreiner, Shaw→Shea, Snyman→Soggin, Whiston→White(Crawford) 등.
- 총 197항목 (8/23 청크). 대시보드 자동빌드 정상.
- **체계 변화**: 커맨더 세션(`00_COMMANDER.md`) 수립 — 데이터=Claude(정제/reclass), 화면=Codex, 지휘=커맨더로 역할 분리. Codex 연동은 `mcp__codex-mcp__codex` MCP 직접호출로 전환(2026-07-17).
- 확보완료(HELD_ALREADY) 시각 구분 UI를 Codex에 위임(WO-001) → 완료, 검증 후 push.
- 다음: C-01 (Samson, 133건)

### 2026-07-14 · 세션 7 (E-01 + GitHub 연결)
- **E-01 (Gideon·Abimelech, 61행) DONE** — Sonnet 백그라운드 위임. 61→**55 고유**(병합 6건: OCR저자분기+정렬밀림 혼합).
- ★고위험 저자정정 1건 메인세션 재검증: `Vincent`→**Mžik, Hans von**(WZKM 29, 1915) — Google Books+JSTOR 교차확인, B→A 승격.
- 등급 A38/B13/C4, UNRESOLVED 0.
- **GitHub 연결 완료**: origin=https://github.com/jtthw64-create/judges-report (사용자가 Codespace로 저장소 생성). 로컬 repo와 원격 초기README를 `--allow-unrelated-histories`로 병합 후 push.
- 총 139항목 (7/23 청크). 대시보드 자동빌드 정상.
- 다음: D-01 (Deborah·Jael·Barak, 62건)

### 2026-07-14 · 세션 6 (F-01 Sonnet 위임 + 인프라)
- **F-01 (Jephthah, 35건) DONE** — **Sonnet 서브에이전트** 위임(토큰 최적화), 메인 검토. → `worklist/F-01.csv`
- 저자정정 다수(bib+웹 검증): Boecktr→Böhler, Dtn→Groß(자기인용), Ewald→Exum, Lohfink→MacDonald, 연도정정 2건. 등급 A19/B13/C3, UNRESOLVED 0.
- ★**데이터 정합성 버그 수정**: download_queue 헤더에 `cited_by` 누락 → DictReader 밀림으로 대시보드 notes 유실되던 문제. 헤더 17컬럼으로 정정 + G-01-022 title 콤마 escape. 재빌드 후 warn 24·info 46 복구.
- **인프라**: git init + 첫 커밋(로컬). `build_dashboard.py`가 `index.html`(Pages 진입점)도 생성. README 작성.
- **결정 반영**: Sonnet 전환 / GitHub Pages+Sheets 병행 / 클라우드 이전(GitHub). 원본 서지는 repo 제외(공유폴더 유지).
- 다음: E-01 (Gideon·Abimelech, 61건)

### 2026-07-13 · 세션 5 (G-01 + 대시보드 자동빌드)
- **G-01 (Micah·Danites, 24행) DONE** → `worklist/G-01.csv` (전건 RESOLVED)
- 24행 → **22 고유** (중복병합 2쌍: Faraone/Faraont, Na'aman/Na'oman)
- ★공저자 정정: `Cox` → **Cox & Ackerman**(bib_sasson). 웹으로 5건 A등급 승격(Amit VT40·Faraone JNES64 DOI·Malamat Biblica51·Na'aman VT55·Suriano JNES66 DOI).
- **자동화:** `build_dashboard.py` 도입 — `download_queue.csv` → `download_dashboard.html` 자동생성. warn/info·정렬·통계 자동. 이후 수기편집 폐지.
- 다음: F-01 (Jephthah, 35건)

### 2026-07-13 · 세션 4 (방법론 확정 + H-01)
- confidence(A/B/C) 소급: `download_queue.csv`, 대시보드 반영. `40_검증방법론.md` 박제.
- **H-01 (Gibeah, 17행) DONE** → `worklist/H-01.csv` (전건 RESOLVED)
- **bib 원본 우선 대조** 첫 적용 — 매우 효과적. 잘린 제목 다수 복원(Krisel·Owens·Ziolkowski·Revell 등).
- ★**저자 오기 적발**: `Maier 1971`→실제 **Malamat**(WHJP III Judges) — bib_sasson 893행 + 웹 확정.
- 서지 완성: Edenburg(TAU diss 2003), Miller(VT 25), Schunck(BZAW 86 DOI), Na'aman(ZAW 121).
- 등급: A 4건(Miller·Schunck·Malamat + I-01 Knauf 계열), 대부분 B, C 3건(Kedar-Kopfstein ThWAT 표제어미상·Sinclair AASOR·).
- 관찰: **Groß 인용분은 bib 원본(bib_gross 부재)이 약해 웹 의존↑** → C·미확정 비율 높음.
- 다음: G-01 (Micah·Danites, 24건)

### 2026-07-13 · 세션 3 (I-01 + 산출물 형태 확정)
- **I-01 (Ehud, 6행) DONE** → `worklist/I-01.csv`
- 5건 RESOLVED + **1건 UNRESOLVED**(OCR 병합, `worklist/UNRESOLVED.csv`)
- ★**저자 오기 2건 적발**: `Hurowitz 2009`→실제 **Sasson**(FS Oded), `Smith 1942`→실제 **Soggin 1989**(VT 39). + Knauf 쪽수 `254+`→`25-44` 정정.
- 교훈: xlsx **저자·연도 필드 자체가 신뢰 불가**한 사례 다수 → 성씨+연도 매칭의 근본 취약. 웹 대조 필수 확인.
- **산출물 형태 확정**: `download_queue.csv`(15컬럼, access_link·xlsx_ref 포함) + `download_dashboard.html`(클릭 접근링크·원본엑셀 좌표·받음 체크 localStorage).
- 다음: H-01 (Gibeah, 17건)

### 2026-07-13 · 세션 2 (J-01)
- **J-01 (Shamgar, 5행) DONE** → `worklist/J-01.csv` · download_queue 편입
- 5원행 → **4 고유항목** (Fensham·Mazar·Scherer·van Selms)
- ★**중복병합 발견**: `Seims 1964`(Groß) + `Selms 1964`(Sasson) = 동일 논문 van Selms "Judge Shamgar" VT 14. OCR 저자분기로 xlsx가 2행으로 분리 → 성씨+연도 매칭이 못 잡음. **전체 2395에 유사 OCR 중복 다수 존재 추정** → 후속 배치에서 병합 주의.
- ★**잘린 제목 복원**: Scherer 원행 `...ursprünglichen Positio`(잘림) → 웹으로 완전제목+ZAW 114 (2002) 106-109 복원.
- DOI 확보: Mazar `10.1179/peq.1934.66.4.192`.
- 바운더리 보강: **PEQ(Palestine Exploration Quarterly)를 OT-검색바운더리에 표적으로 추가**(52종). Mazar 항목 boundary off-list→표적 소급 정정.
- 다음: I-01 (Ehud, 6건)

### 2026-07-13 · 세션 1 (K-01 파일럿)
- **K-01 (Tola·Jair, 1건) DONE** → `worklist/K-01.csv`
- 확장 CSV 포맷 확정: 정제(17컬럼) = 서지 정규화 + boundary 태깅 + id_type/identifier + status + notes
- 처리 내역: Knauf 1995 "Jair" — OCR교정(`NBL ll`→`NBL II`), 실재 확인(Knauf 실존·NBL 실재), status=RESOLVED, boundary=off-list(사전, 보류)
- 관찰: 사전 표제어는 DOI 없음 → ISBN/전집 단위 식별. off-list 처리 규칙 검증됨.
- 다음: J-01 (Shamgar, 5건)

### 2026-07-13 · 세션 0 (셋업)
- 데이터 검증 완료 (`2026-07-13_missing검증_및_수집워크플로우.md`)
- 검색 바운더리 확보 (`OT-검색바운더리.md`)
- 진행 순서·배치 계획 수립 → **가벼운 것부터, 사사기 핵심 우선**으로 확정
- 인계 문서 세트 생성 (`00_START_HERE.md`, 본 트래커)
- **정제 미착수.** 다음 세션 시작점 = K-01
