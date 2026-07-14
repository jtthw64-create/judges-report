---
title: 인수인계 — 다른 PC로 세션 이전
type: handoff
updated: 2026-07-14
---

# 00-B · 다른 PC로 옮기기 (인수인계)

이 프로젝트는 **두 곳**에 걸쳐 있다. 새 PC에서는 **둘 다** 접근 가능해야 이어서 작업할 수 있다.

| 구분 | 위치 | 내용 | 새 PC 접근 조건 |
|---|---|---|---|
| **A. 원본 서지** | Google Drive `5 Book 3 Judges Resources/` (읽기전용) | `Judges_missing_by_character.xlsx`, `bib_sasson.md`, `bib_smith.md`, `MISSING_*.md` | **jtthw64@gmail.com 구글드라이브 계정이 새 PC에 마운트**되어 있어야 함 (Google Drive 데스크톱 앱 로그인) |
| **B. 가공 산출물** | `judges report/` (로컬 git + GitHub) | 계획·CSV·대시보드·방법론 문서 전부 | GitHub repo clone, 또는 A와 같이 Drive 동기화로도 접근 가능 |

⚠️ **A가 없으면 Track 1 신규 정제(bib 원본 대조)가 불가능하다.** B(GitHub)만 있으면 "지금까지 한 것 확인"은 되지만 "다음 배치 이어서 처리"는 못 한다. 새 PC에서 반드시 Drive 계정부터 확인할 것.

## 새 PC 체크리스트
1. **Google Drive 데스크톱 앱**에 `jtthw64@gmail.com` 로그인 → `내 드라이브/Claude Cowork GD/` 경로 동기화 확인.
   - 경로는 OS·사용자명에 따라 다름 (이 PC 기준: `/Users/nurikim/Library/CloudStorage/GoogleDrive-jtthw64@gmail.com/내 드라이브/Claude Cowork GD/`). 새 PC에서 실제 경로를 다시 확인해 이후 작업에 반영할 것.
2. **git** 설치 확인. **GitHub 인증**: 새 PC는 자격증명이 없으므로 `git clone https://github.com/jtthw64-create/judges-report.git` 시 로그인 필요 (브라우저 인증 또는 PAT).
   - 단, B가 이미 A 안(Drive)에도 실물로 존재하므로(`judges report/` 폴더 자체가 Drive 하위) **Drive만 동기화되면 GitHub clone 없이도 바로 이어받기 가능**. GitHub는 백업·배포·다른 사람 열람용.
3. **Python 3 + openpyxl**: `pip3 install openpyxl` (xlsx 원본 읽기용).
4. **Claude Code**를 `judges report/` 상위 폴더(`Claude Cowork GD/`)에서 실행.

## 이어받는 순서 (새 세션 첫 메시지 기준)
1. 이 문서로 A·B 접근 확인.
2. `00_START_HERE.md` — 규칙·문서맵.
3. `20_PROGRESS_TRACKER.md` — **다음 액션** 확인 (현재: D-01, Deborah·Jael·Barak 62건).
4. `10_진행순서_배치계획.md` — 배치 정의. `40_검증방법론.md` — 정제 절차·신뢰등급.
5. 정제 후 `worklist/download_queue.csv` append → `python3 build_dashboard.py` → git commit.

## 현재 스냅샷 (2026-07-14)
- **진행:** 7/23 청크 완료 (K·J·I·H·G·F·E), download_queue **139항목**, UNRESOLVED 1건.
- **모델:** 대량 정제는 **Sonnet 5**(서브에이전트 위임)로 전환 완료. Opus는 설계·의심항목 재검증만.
- **GitHub:** `https://github.com/jtthw64-create/judges-report` 연결·**push 완료**(2026-07-14). SSH 인증 등록됨(`~/.ssh/id_ed25519.pub`, 새 PC는 별도 키 등록 필요 — 방법 B: Terminal.app에서 `git push` 시 브라우저 인증 유도, 또는 새 PC의 공개키를 GitHub Settings→SSH keys에 추가).
  - remote는 SSH(`git@github.com:...`)로 설정됨. HTTPS는 이 환경(비대화형 셸)에서 인증 불가했음.
- **배포(대시보드 공유):** GitHub Pages 활성화 완료(2026-07-14) — **https://jtthw64-create.github.io/judges-report/**. Google Sheets 병행은 아직 미착수.
- **다음 배치:** D-01 (Deborah·Jael·Barak 4-5, 62건).
- **일일 자동 정제 스케줄** 등록됨(2026-07-14): `judges-report-daily-refinement`, 매일 14:00 KST 사용자에게 승인 여부 확인 후 청크 최대 3개 정제. 큐: `worklist/refinement_queue.md`, 로그: `50_정제_이벤트로그.md`.

## 공개 범위 정책 (2026-07-14 확정)
- **repo는 public.** `judges report/` 폴더(가공 산출물: 계획·CSV·대시보드·방법론 문서)는 공개 가능 — 실제로 이미 public repo로 운영 중.
- **원본 자료는 GitHub에 절대 업로드하지 않는다.** `5 Book 3 Judges Resources/`(원본 서지·PDF·xlsx)는 애초에 이 git 저장소 추적 대상이 아니며, Google Drive에만 존재(읽기전용). 앞으로도 원본 파일을 `judges report/` 안으로 복사해 커밋하는 일이 없도록 주의.

## 주의사항 (누적)
- 대상 폴더 `5 Book 3 Judges Resources/`는 항상 읽기 전용.
- `download_queue.csv` 컬럼 순서 고정(17개, `40_검증방법론.md`·`20_PROGRESS_TRACKER.md` 참고) — 컬럼 어긋나면 대시보드 데이터 유실(과거 1회 발생·수정됨).
- OCR 저자분기 중복, 저자 정렬밀림 오기가 배치마다 나옴 → bib 원본 우선 대조 원칙 유지.
