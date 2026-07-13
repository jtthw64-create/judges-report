---
title: 정제 할일 큐 (일일 자동 진행용)
type: queue
updated: 2026-07-14
---

# 정제 할일 큐

`daily-refinement-check` 스케줄 작업이 매일 위에서부터 `status: pending`인 청크를 최대 3개까지 꺼내 처리한다.
처리 순서는 `20_PROGRESS_TRACKER.md`의 진행# 순서와 동일(가벼운 것부터 → 무거운 순).

## 규칙
- 하루 처리 한도: **청크 3개**.
- 사용자가 그날 승인하지 않으면 그 날은 건너뛰고 큐는 그대로 유지(자동으로 다음날 재시도).
- 청크 완료 시 이 파일의 해당 행 `status`를 `done`으로, 완료일을 기입.
- 청크 상태는 `20_PROGRESS_TRACKER.md` 배치 현황 표와 항상 일치시킬 것(이중 관리 — 불일치 발견 시 트래커를 정본으로 취급).

## 큐 (진행 순서)

| 순번 | 청크 | 카테고리 | 건수 | status | 완료일 |
|---|---|---|---|---|---|
| 8 | D-01 | Deborah·Jael·Barak | 62 | pending | |
| 9 | C-01 | Samson | 133 | pending | |
| 10 | B-01 | Book·Composition | ~110 | pending | |
| 10 | B-02 | Book·Composition | ~110 | pending | |
| 10 | B-03 | Book·Composition | ~102 | pending | |
| 11 | A-01 | General·ANE | ~150 | pending | |
| 11 | A-02 | General·ANE | ~150 | pending | |
| 11 | A-03 | General·ANE | ~150 | pending | |
| 11 | A-04 | General·ANE | ~150 | pending | |
| 11 | A-05 | General·ANE | ~150 | pending | |
| 11 | A-06 | General·ANE | ~150 | pending | |
| 11 | A-07 | General·ANE | ~150 | pending | |
| 11 | A-08 | General·ANE | ~150 | pending | |
| 11 | A-09 | General·ANE | ~150 | pending | |
| 11 | A-10 | General·ANE | ~150 | pending | |
| 11 | A-11 | General·ANE | ~150 | pending | |
| 12 | A-12 | General·ANE | ~79 | pending | |

남은 16청크. 하루 3청크 처리 시 약 5~6일 소요 예상(승인 거부일 제외).
