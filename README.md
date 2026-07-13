# Judges Resources — 자료 수집 프로젝트

홍교수님(공유 폴더 주인)의 조교 작업으로, 사사기 3개 주석서(Sasson AYB · Smith Hermeneia · Groß Richter)가
인용했으나 드라이브에 없는 자료를 검색·확보해 업데이트하는 프로젝트.
목표: **학계 주요 논의를 누락 없이, 가짜 없이** 확보.

## 📊 다운로드 대장 (GitHub Pages)
> 배포 후 링크: `https://<사용자>.github.io/<repo>/`
`index.html` = 다운로드 대장 뷰. 정본 데이터는 `worklist/download_queue.csv`.

## 🔄 세션 인계 (어느 환경이든 이어받기)
1. `00_START_HERE.md` — 규칙·문서맵·현재 상태
2. `20_PROGRESS_TRACKER.md` — 진행 상태·다음 배치 (세션마다 갱신)
3. `10_진행순서_배치계획.md` — 처리 순서, 배치 정의
4. `40_검증방법론.md` — 오류 원인·확정 절차·신뢰등급(A/B/C)
5. `30_수집전략_2트랙.md` — Track1(미보유)+Track2(발굴)

## 📁 구조
```
judges report/
├── 00_START_HERE.md          진입점
├── 10_진행순서_배치계획.md
├── 20_PROGRESS_TRACKER.md    진행 추적 (핵심)
├── 30_수집전략_2트랙.md
├── 40_검증방법론.md
├── OT-검색바운더리.md         검색 대상 저널·시리즈
├── build_dashboard.py        CSV → 대시보드 자동생성
├── index.html                Pages 진입점 (자동생성)
├── download_dashboard.html   대시보드 (자동생성)
└── worklist/
    ├── download_queue.csv    정본 다운로드 목록
    ├── UNRESOLVED.csv        식별 실패 격리
    └── <청크>.csv            배치별 정제 결과
```

## 🛠 대시보드 갱신
```bash
python3 build_dashboard.py   # download_queue.csv -> index.html + download_dashboard.html
```

## ⛔ 규칙
- 원본 공유 폴더 `5 Book 3 Judges Resources/` 는 **읽기 전용**.
- 서지는 지어내지 않음. 확인 강도는 신뢰등급(A/B/C)으로 표기.
- 다운로드·외부발송·삭제는 사용자 승인 후.

## 원본 자료 주의
원본 서지(`xlsx`, `bib_*.md`)는 홍교수님 자료다. 이 repo에는 **가공 산출물만** 포함하며,
public 공개 시 서지 목록 노출에 유의(민감하면 private repo 사용).
