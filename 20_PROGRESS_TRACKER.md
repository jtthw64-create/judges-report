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
| 10 | B-01 | Book·Composition | ~110 | DONE | 2026-07-17 | worklist/B-01.csv (a/b/c 3분할 병합) |
| 10 | B-02 | Book·Composition | ~110 | DONE | 2026-07-17 | worklist/B-02.csv (a/b/c 3분할 병합) |
| 10 | B-03 | Book·Composition | ~102 | DONE | 2026-07-17 | worklist/B-03.csv (a/b/c 3분할 병합) |
| 11 | A-01 | General·ANE | ~150 | DONE | 2026-07-17 | worklist/A-01.csv (a/b/c 3분할 병합) |
| 11 | A-02 | General·ANE | ~150 | DONE | 2026-07-17 | worklist/A-02.csv (a/b/c 3분할 병합) |
| 11 | A-03 | General·ANE | ~150 | DONE | 2026-07-17 | worklist/A-03.csv (a/b/c 3분할 병합) |
| 11 | A-04 | General·ANE | ~150 | DONE | 2026-07-18 | worklist/A-04.csv (a/b/c 3분할 병합) |
| 11 | A-05 | General·ANE | ~150 | DONE | 2026-07-18 | worklist/A-05.csv (a/b/c 3분할 병합) |
| 11 | A-06 | General·ANE | ~150 | DONE | 2026-07-18 | worklist/A-06.csv (a/b/c 3분할 병합) |
| 11 | A-07 | General·ANE | ~150 | DONE | 2026-07-19 | worklist/A-07.csv (a/b/c 3분할 병합) |
| 11 | A-08 | General·ANE | ~150 | DONE | 2026-07-19 | worklist/A-08.csv (a/b/c 3분할 병합) |
| 11 | A-09 | General·ANE | ~150 | DONE | 2026-07-19 | worklist/A-09.csv (a/b/c 3분할 병합) |
| 11 | A-10 | General·ANE | ~150 | DONE | 2026-07-20 | worklist/A-10.csv (a/b/c 3분할 병합) |
| 11 | A-11 | General·ANE | ~150 | DONE | 2026-07-20 | worklist/A-11.csv (a/b/c 3분할 병합) |
| 11 | A-12 | General·ANE | ~79 | DONE | 2026-07-20 | worklist/A-12.csv (a/b/c 3분할 병합) |

**집계:** 완료 **23 / 23청크 (전량 완료)** · 처리(원행) **2395 / 2395건** · download_queue **2277항목**(HELD_ALREADY 72 포함) · UNRESOLVED 35

## 다음 액션
→ **정제 단계 전량 완료(2026-07-20).** 23/23 청크 done, 원행 2395건 전건 처리. 일일 정제 예약 스케줄(`judges-report-daily-refinement`)은 큐 소진에 따라 종료·삭제됨(2026-07-19 사용자 사전승인).

**잔여 과제(사용자 지시 시 새 세션에서 착수)**
1. **UNRESOLVED 35건 재식별** — OCR 손상으로 title 특정 실패. 주석서 3권 PDF 실물 참고문헌 대조가 필요(현 extracted/ 텍스트로는 복원 불가).
2. **★boundary 과잉정정 의심 91건 판정** — 2026-07-20 전수 점검에서 `OT-검색바운더리.md` 표와 불일치 발견. 대부분 `통독 → 표적` 방향으로, 표상 **표적**인 UF·AYB·Hermeneia·HSM·ZDPV·JCS·JNES 등이 통독으로 올라가 있다. 2026-07-19 세션의 일괄 정정이 통독 쪽으로 과잉 적용된 것으로 보인다. **대량·되돌리기 어려운 변경이라 무인 회차에서 적용하지 않고 보류**했다. 점검 스크립트는 세션 스크래치패드에 있었으므로 재작성 필요(정규식은 표 전체를 기계적으로 옮기되, 아래 오탐군은 반드시 제외).
   - 확인된 오탐군: `Göttingen:`(출판도시) · `Coniectanea Biblica`/`Biblica et Orientalia`(저널 Biblica 아님) · `Kurzgefasstes exegetisches Handbuch`/`Handkommentar zum AT`(Mohr HAT·Sellin KAT 아님) · `British School of Archaeology in Iraq`(저널 Iraq 아님) · `Anchor (Yale) Bible Reference Library`(사전류, AYB 주석 아님) · `Feminist Interpretation of the Bible` 등 제목 내 일반어 · `Studia Semitica Upsaliensia` · `Sheffield: JSOT Press` · `Subsidia/Analecta Biblica` · `JBL Monograph Series` · `Jewish Theological Seminary`.
   - 3자 이하 약어(VT·AB·HS·ZA·RA·BN 등)는 **뒤에 권호 숫자나 풀네임 병기 괄호가 오는 서지 맥락에서만** 인정할 것. 단독 매칭은 오탐 폭증.
3. **A-12c-003 후속** — R1712 Zadok 1988은 xlsx가 Sasson;Smith 공동인용으로 병합했으나, Smith가 실제 인용한 것은 동일저자·동일연도의 별개 논문(*Biblische Notizen* 42[1988]:44-48). 해당 문헌은 이번 청크 범위 밖이라 행 미생성 — 별도 편입 검토 필요.
4. **실제 자료 수집** — download_queue 2277항목(QUEUED 2205) 기준 다운로드 실행. C등급 113건은 수령 시 원문 최종 확인 필수.

### 2026-07-20 · 세션 14 (A-10/A-11/A-12 9분할 병렬 — 무인 예약 실행 · **큐 소진 최종 회차**)
- **A-10·A-11·A-12 (General·ANE, R1352~R1730, 379행) DONE** — 각 청크 3분할(총 9개) Sonnet 서브에이전트 동시 병렬 위임. 379행 → 서브에이전트 단계 371건 → UNRESOLVED 4건 격리 → **커맨더 교차중복 2건 병합 후 365건 신규 편입**. download_queue **1912 → 2277항목**. UNRESOLVED 31 → 35(+4).
- 청크별: A-10 142건(A101/B27/C14, 병합 4) · A-11 145건(A77/B50/C18, 병합 3) · A-12 78건(A50/B20/C8, 병합 2, HELD 2).
- **통합 단계 검사 3종 전부 통과**: 17컬럼 위반 0건(9개 CSV 및 최종 2277행) · 원행 커버리지 R1352~R1730 전건 1회씩(누락·중복 0) · HELD_ALREADY 72건 전건 `[확보완료:` 경로 보유.
- **교차중복 2건 병합**(4회 연속 발생 — 서브에이전트는 자기 청크만 보므로 구조적으로 못 잡음):
  - `A-10a-010` → `A-03c-013` (Ehrlich 1969 *Mikrâ ki-pheschutô* — 저자명 'Arnold B.' 보강 반영)
  - `A-10c-025` → `B-03b-022` (Smend 1971 *Das Gesetz und die Völker* — **cited_by Groß → Groß;Smith 통합**, access_link를 ADW Göttingen 리포지토리 직링크로 교체)
- **held_audit 전수 재실행(2277행)**: 후보 38건 전부 사람 눈 검증 → **신규 확정 0건**. 오탐 3건 판정 기록: `A-12c-002` Zakovitch 1981 *Woman's Rights* ≠ 파일 *Sisseras Tod*(동일저자·동일연도 별개 논문, 후자는 별도 HELD 처리됨) · `A-12c-012` Zerubavel 1995 ≠ `vanWolde 1995 Yael`(저자 상이, 'Yael' 토큰 오탐) · `D-01-003` Bal 1988 *Murder and Difference* ≠ *Death and Dissymmetry*(Bal의 1988년 별개 저작 2권).
- **저자정정 주요 성과**(전부 원본 대조 + 외부 DB 교차확인):
  - **`Strawn` → Sun Tzu** *The Art of War*(A-11a R1527) — MISSING_Sasson에도 동일 오염이 있었고 `bib_sasson.md` 정제본만 정확했음
  - **`VanderKam` → Van Seters 4건**(A-11b R1595~R1598, *In Search of History* 등) · **`Tov` → Trebolle Barrera 2건**(DJD XIV 개별 항목 집필자 vs 볼륨 편집자 혼동, 원본 bib 자체 오류)
  - **`Younger` → Zakovitch 3건**(A-12c R1706~R1708) · **`Snyman`→Soggin, `Stager`→Stamm 2건**(A-10c) · **`Winckler`→Winton Thomas / Winkler 분리**(A-12b)
  - OCR 손상 복원: `Sttbap`→Seebass 3건 · `Wtippert`→Weippert 2건 · `Vtijola`→Veijola 3건 · `Trapper`→Tropper 4건 · `Ttta`→**Tita**(실존 인물 아님) · `Wlnin`→Wénin · `Smtnd`→Smend · `Vrits`→de Vries
  - 연도 정정: Schorn 1957→**1997**(OCR 9→5) · Spieckermann 1984→1982 · Westenholz 1998→1997(Smith 원본 오류) · Wenham 1996→2000
- **커맨더 정규화**: author 필드 메타표기 6건을 기존 관례 `이름 (추정)`로 통일. 그중 `Whiston, William(역)`은 저자·역자 뒤바뀜 실질 오류로 **`Josephus, Flavius (trans. William Whiston)`** 로 정정. boundary 빈값·'불명' 2건 → off-list.
- **boundary**: 신규분 자동 후보 5건 중 **1건만 적용**(A-11a-022 AThANT → 통독). 나머지 4건은 오탐 판정(AYB *Reference Library*·*Hand*kommentar·게재처 "미상" 추정 2건). **기존 청크 91건은 과잉정정 의심으로 보류 — 위 「다음 액션」 2번 참조.**
- **서브에이전트 공통 제약**: 9개 전부 세션 WebSearch 쿼터(200회)를 소진해 후반부는 WebFetch(Crossref·OpenLibrary·archive.org·Persée API)로 전환. C등급 40건은 대부분 이 한계에 기인하며 notes에 사유 명시됨.
- 대시보드 자동빌드 정상(2277행). **정제 단계 전량 완료 — 예약 스케줄 종료.**

### 2026-07-19 · 세션 13 (A-07/A-08/A-09 9분할 병렬 — 무인 예약 실행)
- **A-07·A-08·A-09 (General·ANE, R902~R1351, 450행) DONE** — 각 청크 3분할(총 9개) Sonnet 서브에이전트 동시 병렬 위임. 450행 → 서브에이전트 단계 437건 → **커맨더 교차중복 5건 병합 후 432건 신규 편입**. download_queue **1480 → 1912항목**. UNRESOLVED 29 → 31(+2).
- 청크별: A-07 146건(A100/B32/C14) · A-08 143건(A116/B24/C3, HELD 4) · A-09 143건(A88/B47/C8, HELD 2).
- ★**커맨더 정정 사항**:
  1. **교차중복 5건 병합**: A-07a-001↔A-06c-049(Layton 1990 — xlsx R901/R902 인접 중복, cited_by Groß;Smith 통합), A-08a-042↔B-02c-019(Mosca 1984 Who Seduced Whom), A-08b-020↔A-03a-014(Vaux 1978 Early History of Israel), A-08c-029↔A-06c-021(Kupper ARM 28), 그리고 **신규 내부** A-07b-017↔A-07a-012(Lemos 2006 — 서로 다른 서브에이전트가 각각 Sasson·Groß 인용분을 잡음). 청크 경계에 걸친 중복은 에이전트가 구조적으로 못 잡는다는 점 3회 연속 재확인.
  2. **병합 안 함(별개 저작)**: Feldman 1998 *Josephus's Interpretation of the Bible*(UC Press) vs A-04a-008 *Studies in Josephus' Rewritten Bible*(JSJSup 58) — 동일 저자·동일 연도지만 별개 단행본.
  3. **A-09c CSV 인용부호 오류 5행 복구**: notes에 콤마가 있는데 큰따옴표로 감싸지 않아 18컬럼으로 깨진 행을 병합·재작성(csv.writer로 quoting 정규화). **17컬럼 검증을 통합 단계 필수 절차로 둘 것.**
  4. **boundary 오분류 132건 일괄 정정**(통독 58 + 표적 74). 2026-07-18의 29건 정정 이후에도 남아 있던 대량 오분류를 저널·시리즈 표 **전체**를 정규식화해 전수 점검. 통독 312→447, 표적 69→236, off-list 1099→1229(신규분 포함). 오탐 12건은 제외 판정(Sheffield **JSOT Press**=출판사 / Subsidia·Analecta **Biblica** / JBL·JSOT Monograph Series / **JTS**=Jewish Theological Seminary 기관명 — 저널 약어와 형태만 같은 것들).
  5. **held_audit 전수 재점검(1912건)으로 소급 누락 4건 추가 발견**: `I-01-002`(Knauf 1991 Eglon and Ophrah), `J-01-002`(Maisler 1934 Shamgar ben ʿAnat), `J-01-003`(Scherer 2002 Simson und Schamgar), `J-01-004`(van Selms 1964 Judge Shamgar) — **모두 `2 Ehud/Nuri added/`·`2 Shamgar/Nuri added/` 하위폴더**. 8-5절이 지적한 `Nuri added` 패턴이 또 나왔다. HELD_ALREADY 60→70, 전건 `[확보완료:` 경로 보유 검증 통과.
  6. xlsx 확보상태 표기: 카테고리 시트 11행 + `전체 All` 11행(J-01-004는 R5·R6 두 행에 걸친 중복 항목이라 양쪽 표기). **CSV의 `xlsx_ref`에서 대상 행을 도출**(2026-07-18 교훈 적용).
- ★고위험 저자정정(off-by-one 밀림 계속):
  - **Groß 인용 독일어 단행본 3건이 통째로 von Rad로 복원**(A-09b, R1262~R1264 — MISSING_Groß는 'Pury'로 표기했으나 신명기 ATD8·Weisheit in Israel·Theologie des AT는 모두 Gerhard von Rad 저작. Pury는 신명기 주석을 쓴 바 없음)
  - **Lenzi 2006 → Le Roux, Nicolas 2006**(A-07a, R915 — 앙리 3세 암살 연구 프랑스사 단행본. 아시리아학자 Lenzi와 무관)
  - **Michalowski → Michel, Cécile 2건**(A-07c, R1046/R1047) · **Ogden → Olmo Lete 2건**(A-08c) · **Rippin→Römheld, Roje→Rofé 3건**(A-09c)
  - **★원본 bib 자체가 틀린 사례 첫 확인**: R1144 "Neumann 2002 Taanach und Megiddo"는 bib_sasson·MISSING_Sasson **양쪽 원본에 모두 'Neumann'으로 오기**되어 있어 1단계만으로는 못 잡고 academia.edu 저자 업로드본에서만 발견(**Niemann, Hermann Michael**, VT 52). 2단계 외부 DB 검증이 장식이 아님을 반대 방향에서 입증.
  - 기타: Persian 1998→Feldman, Nashville 1978→Vaux(도시명이 저자 자리), Oblata→Kupper(실재하지 않는 이름), Polzin 2003→Preuss 1971, Piter/Reni→Peter/René(애너그램형 OCR), Maier→Malamat 2건·Meier 1건, Milgrom→Miller, Mitchell→Mittmann, Mosis 1984→Mosca, Na'aman 2013→Nadali, Nelson 1994→Neudecker, Nabokoy→Nachmanides/Nabokov 분리, Hvidberg류 연도모순 2건(Parker 2003→1997, Rofé 1885→1982, Root 1994→1979).
- 대시보드 자동빌드 정상(1912행). 다음: **A-10~A-12** (General·ANE, ~379행 잔여 — 시트 R1352~R1730)

### 2026-07-18 · 세션 12 (A-04/A-05/A-06 9분할 병렬 — 무인 예약 실행)
- **A-04·A-05·A-06 (General·ANE, 450행) DONE** — 각 청크 3분할(총 9개) Sonnet 서브에이전트 동시 병렬 위임. 450행 → 서브에이전트 단계 434건 → **커맨더 교차중복 5건 병합 후 429건 신규 편입**. download_queue **1051 → 1480항목**. UNRESOLVED 20 → 29(+9).
- 청크별: A-04 144건(A115/B25/C4, HELD 4) · A-05 140건(A112/B24/C4) · A-06 145건(A98/B43/C4, HELD 2).
- ★**커맨더 정정 사항**:
  1. **교차중복 5건 병합**(신규 행 폐기·기존 행에 cited_by 통합): A-04b-043↔B-01c-030(Gaß 2005 Ortsnamen), A-05a-034↔A-01b-029(Hallo 2004 Achsah), A-05b-019↔B-02a-031(Hess 1997 4QJudg), A-06a-031↔A-01b-040(Barthélemy 1982 OBO 50/1), A-06b-027↔B-02b-020(Klein 1999 Achsah). 9개 에이전트가 각자 청크만 봐서 **기존 큐와의 중복은 구조적으로 못 잡는다** — 통합 단계 교차대조가 필수임을 재확인.
  2. **held_audit 전체 재실행(1480건)으로 확보완료 2건 추가 발견**: `A-04b-016`(Fritz 2006, Maeir–de Miroschedji FS 수록 — 원본이 챕터 제목 절단이라 에이전트가 못 잡음. 보유 파일명으로 **제목까지 복원**), `A-03b-026`(Groß 1998 SBS 176 — **A-03 정제 시 누락**, `Nuri added` 하위폴더에 서명 전체가 파일명인 형태라 성씨+연도 매칭이 약했음). HELD_ALREADY 58→60, 전건 `[확보완료:` 경로 보유 검증 통과.
  3. **boundary 오분류 29건 일괄 정정**(9-4절 유형 재발): VTSup·BZAW·LHBOTS·JSOTSup·OBO·WMANT·FRLANT·BWANT·AThANT 소속인데 `off-list`/`표적`으로 잘못 분류돼 있던 행. 이번 배치 신규분뿐 아니라 **A-01~A-03·B·C·I 등 기존 청크분이 대다수** — FAT 7건 정정(2026-07-17)이 FAT만 고치고 끝난 탓. 통독 283→312.
  4. **xlsx 표기 오류 자체 발견·복구**: 서브에이전트 산문 보고의 ID 오기(`R508(=A-04b-008)`, 실제 CSV는 A-04b-007=R508)를 그대로 믿어 R509(Noth 1957, 미확보)에 `완료`를 찍었다가 회수하고 R508에 정표기. **교훈: xlsx 반영 대상은 산문 보고가 아니라 CSV의 `xlsx_ref`에서 도출할 것.**
- ★고위험 저자정정(전형적 off-by-one 대량 적발):
  - **Hurowitz→Sasson 5건**(A-05c, R728~R732 — 인접 6행 중 5행이 오귀속. Sasson 본인 자기인용이 Hurowitz로 밀린 형태)
  - **"Freunden"→Noth, Martin 5건**(A-04b, R507~R511 — Groß bib OCR 손상 구간. R507은 사사 직무론 핵심 논문 Festschrift Bertholet 1950으로 신규 식별)
  - **Jenni→Jeremias/Jericke 6건 + Jonker→Joosten·Kasher→Katz**(A-06a, 알파벳 인접 밀림 10건)
  - 기타: Fischer 1975→Fleishman 2006, Fischer 1985→Floss 1985, Fnuell 1993→Fewell&Gunn 1990, Josue→Barthélemy(제목 첫 단어를 저자로 오인), Language 1965→Astour, Herdner→Hess, Handy→Haran, Hvidberg 2002→Irsigler(Hvidberg는 1890년 사망 — 저작 불가능), Green→Greenberg, Globt→Görg, Ishida 1971→Israel Museum(기관저자).
- 대시보드 자동빌드 정상(1480행). 다음: **A-07~A-12** (General·ANE, ~829행 잔여)

### 2026-07-17 · 세션 11 (A-01/A-02/A-03 9분할 병렬 — 무인 예약 실행, 승인 대기 없음)
- **A-01·A-02·A-03 (General·ANE·Other, 450행) DONE** — 각 청크 3분할(총 9개) Sonnet 서브에이전트 동시 병렬 위임. 450행 → **431 확정 고유**(QUEUED 428, HELD_ALREADY 3), UNRESOLVED 8건 추가(총 20).
- 등급 A367 / B53 / C11. download_queue **620 → 1051항목**.
- ★**커맨더 정정 사항**(서브에이전트 결과 검토에서 발견·수정):
  1. **A-01c 재작업**: 담당 에이전트가 "원본 bib 파일 없음"을 이유로 **1단계(원본 대조)를 통째로 생략**하고 외부 DB만으로 확정 → 원인은 커맨더 프롬프트의 경로 오류(`{WD}/judges-index/` ≠ 실제 `5 Book 3 Judges Resources/judges-index/`). 올바른 경로로 재작업 지시 → **A등급 29→44 상향, UNRESOLVED 2→1**(R121 Bekkum→Benz 1972 해결·R128 병합), 제목 다이어크리틱·어순 오류 9건 추가 정정.
  2. **중복 7건 고유화**: Bader 1994(R66/R72), Bal 1987(R77/R81), Brenner 1990(R184/R192), Brichto Curse(R196 1963초판/R197 1968재간), Ephʿal 2009 **3중복**(R424/R425/R430), Faber 1992(R444/R447). 서브에이전트들이 중복을 인지하고도 행을 남겨둔 것을 커맨더가 병합(cited_by 통합·ℹ중복병합 note 기재).
  3. **별개 문헌 판정(병합 안 함)**: IDB 본편(Buttrick 1962, 4vols) vs IDB **보유판**(Crim 1976 Supplementary) / Dossin ARM **1권**(1950) vs **4권**(1951) — 제목이 동일해 중복으로 보이나 실제 별개 자료.
  4. **병합 중 자체 실수 발견·복구**: Bal 1987 병합 시 `[확보완료:]` 경로를 가진 쪽(R81) 행을 버려 경로가 유실 → 복구 후 **HELD_ALREADY 53건 전수 검증**(전건 경로 보유 확인).
  5. **데이터 오류 정정**: A-01b-036 author 필드에 `Barron, [PhD diss.]`가 들어가 있던 것 → `Barron`으로 정정(이름·수여대학 미확정은 notes에 ⚠ 표기).
- ★고위험 저자정정 다수(전형적 off-by-one): **Van Seters 클러스터 5건**(xlsx 전부 'Bachmann'→Van Seters, 단 R68은 DDD 사전이라 van der Toorn/Becking/van der Horst 편으로 별도 확정), **Groß 자기인용 7건**('Dtn' 클러스터), **Zenger/Hossfeld**(가짜 저자명 'Exegese'에서 복원), Braude→Brenner, Brenner→Brettler, Cambridge→Cross, Drews→Dubovský, Ewald→Exum, Alter→Álvarez Barredo, Dalman→Da Riva/Lang/Fink, Darton(출판사명)→de Vaux 등.
- **확보완료 재점검**: `worklist/held_audit.py`를 1051건 전체 재실행 → **신규 매칭 0건**(유일 score=1인 Bal 1988 "Murder and Difference"↔파일 "Death and Dissymmetry"는 동일저자·동일연도 **다른 저작**으로 기존 배제 판정 유지). xlsx 사본 확보상태 표기: 카테고리시트 5행 + 전체All 5행.
- 대시보드 자동빌드 정상(1051행). 다음: A-04~A-12 (General·ANE, ~1279행 잔여)

### 2026-07-17 · 세션 10 (B-01/B-02/B-03 9분할 병렬 — 예약작업 충돌 없이 완료)
- **B-01·B-02·B-03 (Book·Composition·Framework, 322행) DONE** — 각 청크를 3분할(총 9개) Sonnet 서브에이전트로 동시 병렬 위임, 12:12~12:31 KST(약 20분)에 전부 완료. 322행 → **300 확정 고유**(HELD_ALREADY 20, QUEUED 280), UNRESOLVED 4건 추가(B-01a 3건, B-01c 1건).
- 등급 A231/B64/C5.
- **14:00 예약 정제작업과 충돌 방지**: 착수 즉시 `worklist/refinement_queue.md`에서 B-01/02/03을 `in_progress`로 잠그고 push → 예약작업이 있었다면 자동으로 건너뛰도록 조치. 12:32 KST에 전 작업(취합·재점검·커밋)을 마쳐 실제로 14:00 이전 종료.
- **확보완료 재점검**: `worklist/held_audit.py`를 620건 전체에 재실행 → 신규 누락 없음 확인(기존에 배제 판정한 애매 케이스만 재확인됨, B-01a-005 Amit 1999는 서브에이전트가 이미 "다른 저작"으로 정확히 배제).
- ★고위험 저자정정 다수: Groß 2021 원서 Literaturverzeichnis PDF를 직접 열람해 MISSING_Groß.md의 절단 문제를 상당 부분 해소(B-01b). Sasson, Jack M. 본인 자기인용 2건 추가 적발(B-02b, 8-5절 유형 반복).
- 총 **620항목** (12/23 청크, HELD_ALREADY 50, UNRESOLVED 12). 대시보드 자동빌드 정상.
- 다음: A-01~A-12 (General·ANE, 총 ~1729건 잔여 — 프로젝트 최대 분량대)

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
