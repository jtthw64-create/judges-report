---
title: 대시보드 감시루프 프롬프트 (세션마다 재등록용)
type: reference
updated: 2026-08-01
---

# 감시루프 재등록 방법

새 세션이 시작되면 **`CronCreate`로 아래 프롬프트를 그대로 등록**한다.
- `cron`: `7 * * * *` (매시 07분 — 정시 몰림 회피)
- `recurring`: `true`
- 세션 전용이라 세션 종료 시 사라진다. 최대 7일 후 자동 만료.

등록 **전에** 밀린 pending이 있는지 1회 수동 점검할 것(세션 공백 동안 쌓였을 수 있음).

---

## 프롬프트 전문 (그대로 복사해 CronCreate의 prompt로)

```
Judges 대시보드 감시루프(v3 — pending reclass 임계값 20분으로 하향, 1시간 간격 점검 시 놓치는 사각지대 방지). 다음을 조용히 수행하고, 이상이 없으면 채팅에 아무 메시지도 보내지 마라(무응답으로 종료). "judges report" 작업 폴더(Google Drive: "Claude Cowork GD/judges report")로 이동.

1. `worklist/monitor_state.json`을 읽어 last_row_count를 확인(없으면 0).
2. 리다이렉트를 따라가며 백엔드 이벤트를 조회한다(POST 없이 GET이므로 curl -s -L 그대로 사용 가능):
   `curl -s -L "https://script.google.com/macros/s/AKfycbzUwrljKotJQSPBTZn6_WbMFfjsdvAoozgO2TnJ2wnUUvF9xPxG6ZciYfY3DRmY44ZugQ/exec"`
   응답은 `{"ok":true,"rows":[{ts,kind,id,field1,field2,field3}, ...]}`.
3. rows 개수가 last_row_count보다 늘었으면, 새로 추가된 행만 검사해 "문제"인지 판단:
   - kind가 got/priority_change/reclass/prof/unavailable/bd_override/restype_change 중 하나가 아닌 미인식 kind → 문제 (Apps Script doPost 미처리 가능성).
   - kind가 reclass인데 field1(사유)이 비어있음 → 문제 (재검토 신청 사유 누락, textarea 버그 재발 의심).
4. **추가 점검(매회 항상 수행, rows 증가 여부와 무관)**: 전체 rows에서 kind="reclass"인 이벤트를 id별로 최신(ts 최대) 것만 남긴 뒤, field2(status)가 "pending"인 항목을 모두 추출한다. 그 ts가 현재 시각 기준 **20분 이상 경과**했으면 → 문제("STALE_PENDING_RECLASS", id, ts, 사유 요약). (임계값을 60분→20분으로 낮춤: 점검 주기가 1시간이라 60분 임계값으로는 타이밍에 따라 최대 2시간 가까이 방치될 수 있었음 — 20분이면 매 정시 점검마다 반드시 걸러진다.)
5. 문제로 판단된 항목이 하나라도 있으면 이 채팅으로 간결하게 보고(어떤 kind/id/ts에 어떤 이상인지, STALE_PENDING_RECLASS면 사유 원문 요약 포함). 문제 없으면 침묵.
6. rows 개수를 last_row_count로 `worklist/monitor_state.json`에 갱신 저장(last_check는 현재 처리 시각 문자열). git commit/push는 하지 마라(상태 파일은 로컬 추적용).
7. 이 크론잡은 세션 종료 시 또는 7일 후 자동 만료된다는 점을 스스로 신경쓸 필요 없음 — 단순히 매회 위 점검만 수행.
```

---

## 실제 점검 스크립트 (매 회차 실행하는 것)

⚠️ **POST는 `curl -L`로 안 된다** — Apps Script가 302로 `script.googleusercontent.com`에 넘기는데 리다이렉트에서 메서드가 유실된다. 아래처럼 **Location 헤더를 뽑아 그 URL을 GET**하는 2단계 방식을 쓸 것.

```python
import json, subprocess
from datetime import datetime, timezone

state = json.load(open('worklist/monitor_state.json'))
last = state.get('last_row_count', 0)

head = subprocess.run(['curl','-s','-o','/dev/null','-D','-',
    'https://script.google.com/macros/s/AKfycbzUwrljKotJQSPBTZn6_WbMFfjsdvAoozgO2TnJ2wnUUvF9xPxG6ZciYfY3DRmY44ZugQ/exec'],
    capture_output=True, text=True).stdout
loc = [l.split(': ',1)[1].strip() for l in head.splitlines() if l.lower().startswith('location:')][0]
out = subprocess.run(['curl','-s', loc], capture_output=True, text=True).stdout
data = json.loads(out)
rows = data['rows']
new = rows[last:] if len(rows) > last else []

known = {'got','priority_change','reclass','prof','unavailable','bd_override','restype_change'}
problems = []
for r in new:
    kind = r.get('kind','')
    if kind not in known:
        problems.append(('UNKNOWN_KIND', kind, r.get('id'), r.get('ts')))
    elif kind == 'reclass' and not (r.get('field1') or '').strip():
        problems.append(('EMPTY_RECLASS_REASON', kind, r.get('id'), r.get('ts')))

latest = {}
for r in rows:
    if r.get('kind') == 'reclass':
        latest[r.get('id')] = r
now = datetime.now(timezone.utc)
for id_, r in latest.items():
    if r.get('field2') == 'pending':
        ts = r.get('ts','')
        try:
            t = datetime.fromisoformat(ts.replace('Z','+00:00'))
        except Exception:
            continue
        age_min = (now - t).total_seconds()/60
        if age_min >= 20:
            problems.append(('STALE_PENDING_RECLASS', id_, ts, (r.get('field1') or '')[:150], round(age_min)))

state['last_row_count'] = len(rows)
state['last_check'] = 'cron_run_v3'
json.dump(state, open('worklist/monitor_state.json','w'))

print('TOTAL_ROWS', len(rows)); print('NEW_ROWS', len(new)); print('PROBLEMS', problems)
```

## 재검토 처리 후 결과 기록 (POST — 반드시 할 것)

처리하고 이걸 안 보내면 계속 `pending`으로 남아 매 회차 재보고된다.

```python
def post(payload):
    data = json.dumps(payload)
    head = subprocess.run(['curl','-s','-o','/dev/null','-D','-','-X','POST',
        'https://script.google.com/macros/s/AKfycbzUwrljKotJQSPBTZn6_WbMFfjsdvAoozgO2TnJ2wnUUvF9xPxG6ZciYfY3DRmY44ZugQ/exec',
        '-H','Content-Type: application/json','-d', data], capture_output=True, text=True).stdout
    loc = [l.split(': ',1)[1].strip() for l in head.splitlines() if l.lower().startswith('location:')][0]
    print(subprocess.run(['curl','-s', loc], capture_output=True, text=True).stdout)  # {"ok":true} 확인

post({'kind':'reclass', 'id':'<항목ID>',
      'comment':'<사용자 원래 사유 그대로>',
      'status':'ai_reviewed',
      'result':'<판단 요약 — 정정했으면 무엇을 어떻게 고쳤는지, 못 고쳤으면 왜>'})
```

## 처리 표준 절차

재검토를 반영할 때는 매번 이 순서를 지킨다(세션 15에서 정착된 루틴):
1. `worklist/download_queue.csv` 백업 (`cp ... .bak_$(date +%Y-%m-%d_%H%M)`)
2. CSV 수정 → **17컬럼 정합성·중복ID 검사**
3. `python3 build_dashboard.py` 재생성 (`download_queue.csv` diff 0 확인)
4. 백엔드에 `ai_reviewed` POST
5. commit + push → **GitHub Pages 배포까지 curl로 폴링 확인**(반영에 30초~1분 걸림. 로컬 파일만 보고 "됐다"고 판단하지 말 것 — 배포 지연 중인 캐시본을 보고 오판한 적 있음)
