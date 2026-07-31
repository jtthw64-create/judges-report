#!/usr/bin/env python3
# download_queue.csv -> download_dashboard.html 자동 생성
# 사용: (judges report/ 에서) python3 build_dashboard.py
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "worklist", "download_queue.csv")
OUT = os.path.join(HERE, "download_dashboard.html")

# Apps Script Web App 배포 후 이 URL만 채우면 재검토/교수님코멘트/우선순위토글이 서버(Google Sheets)에 저장됨.
# 비어있으면 localStorage에만 저장(기기 간 동기화 안 됨).
SHEETS_ENDPOINT = "https://script.google.com/macros/s/AKfycbzUwrljKotJQSPBTZn6_WbMFfjsdvAoozgO2TnJ2wnUUvF9xPxG6ZciYfY3DRmY44ZugQ/exec"

WARN_KW = ["정정", "난이도", "미상", "확인요"]

# 인용 복사 기능: 저널·시리즈명 SBL 약어 조회 (pdf-rename 스킬 규칙 참고, ../rename-pdf 폴더의
# 참고용 약어표를 빌드 시점에만 읽는다 — 이 judges report 저장소에는 커밋하지 않음).
def _parse_abbrev_table(path, start_marker=None, stop_marker=None):
    out = {}
    if not os.path.exists(path):
        return out
    active = start_marker is None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if start_marker and start_marker in line:
                active = True
                continue
            if stop_marker and stop_marker in line:
                break  # 8.4.2(약어→풀네임 역방향 표) 등 방향이 반대인 섹션은 제외
            if not active:
                continue
            line = line.strip()
            if not (line.startswith("|") and line.endswith("|")):
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) != 2:
                continue
            full, abbr = parts
            if not full or not abbr:
                continue
            if full.lower() in ("full name", "full name / source"):
                continue
            if set(full) <= set("-: "):
                continue
            if len(abbr) > 25 or len(abbr.split()) > 4 or re.match(r"^\d", abbr):
                continue  # PDF 추출 줄바꿈 깨짐으로 인한 오염 행 제외
            out.setdefault(full.lower(), abbr)
    return out

def _resolve_journal_cite(js_raw, table, sorted_items):
    js_raw = (js_raw or "").strip()
    if not js_raw:
        return js_raw
    low = js_raw.lower()
    if low in table:
        return table[low]
    # "Full Name (ABBR)"처럼 이미 약어가 괄호로 병기된 경우: 괄호 앞부분으로 재조회해
    # 표에 있으면 약어로 치환. 괄호 내용이 약어 자체와 같으면 중복이므로 버리고,
    # "(추정)"·"(FS ...)"처럼 약어가 아닌 부가설명이면 정보 손실 없이 그대로 보존한다.
    m = re.match(r"^(.*\S)\s*\(([^()]+)\)\s*$", js_raw)
    if m:
        base_key = m.group(1).strip().lower()
        if base_key in table:
            abbr = table[base_key]
            paren = m.group(2).strip()
            if paren.lower() == abbr.lower():
                return abbr
            return f"{abbr} ({paren})"
    # 저널 풀네임 뒤에 권호·쪽수 등이 그대로 붙어 있는 경우(예: "Zeitschrift für die
    # alttestamentliche Wissenschaft 104/2 (1992): 202–216") — 문자열 맨 앞이 표의
    # 풀네임과 일치하면 그 부분만 약어로 치환하고 나머지(권호·쪽수)는 그대로 둔다.
    # 긴 이름부터 시도해 짧은 이름의 우연한 부분일치를 방지한다.
    for full, abbr in sorted_items:
        if low.startswith(full):
            rest = js_raw[len(full):].lstrip()
            rest = re.sub(rf"^\(\s*{re.escape(abbr)}\s*\)\s*", "", rest, flags=re.IGNORECASE)
            return (abbr + (" " + rest if rest else "")).strip()
    return js_raw

_RENAME_PDF_DIR = os.path.join(os.path.dirname(HERE), "rename-pdf")
JOURNAL_ABBR = _parse_abbrev_table(os.path.join(_RENAME_PDF_DIR, "OT_Journal_Abbreviations.md"))
for _k, _v in _parse_abbrev_table(os.path.join(_RENAME_PDF_DIR, "abbreviations.md"), start_marker="### 8.4.1", stop_marker="### 8.4.2").items():
    JOURNAL_ABBR.setdefault(_k, _v)
_JOURNAL_ABBR_SORTED = sorted(JOURNAL_ABBR.items(), key=lambda kv: -len(kv[0]))

rows = []
with open(CSV, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        conf = (r.get("confidence") or "").strip()
        notes = (r.get("notes") or "").strip()
        status = (r.get("status") or "").strip()
        held_match = re.search(r"\[확보완료:\s*(.*?)\]\s*$", notes)
        held_path = held_match.group(1).strip() if held_match else ""
        warn = info = ""
        if any(k in notes for k in WARN_KW) or conf == "C":
            warn = notes or ("원문 확인 권장" if conf == "C" else "")
        elif notes:
            info = notes
        ident = (r.get("identifier") or "").strip()
        js = (r.get("journal_series") or "").strip()
        if ident and ident not in ("미확정", ""):
            js = f"{js} · {ident}" if js else ident
        rows.append({
            "id": r["id"], "pri": r["priority"], "bd": r["boundary"], "cat": r.get("category") or "",
            "conf": conf, "au": r["author"], "yr": r["year"], "ti": r["title"], "js": js,
            "link": r["access_link"], "ref": r["xlsx_ref"], "status": status,
            "heldPath": held_path, "warn": warn, "info": info,
            "jsRaw": (r.get("journal_series") or "").strip(), "idType": (r.get("id_type") or "").strip(),
            "identifier": (r.get("identifier") or "").strip(),
            "jsCite": _resolve_journal_cite(r.get("journal_series"), JOURNAL_ABBR, _JOURNAL_ABBR_SORTED),
        })

op = {"high": 0, "mid": 1, "low": 2}
oc = {"A": 0, "B": 1, "C": 2}
rows.sort(key=lambda d: (op.get(d["pri"], 3), oc.get(d["conf"], 3), d["au"]))
DATA = json.dumps(rows, ensure_ascii=False)

TEMPLATE = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Judges 다운로드 대장</title>
<style>
  :root{--bg:#f7f7f8;--card:#fff;--ink:#1a1a1a;--sub:#666;--line:#e3e3e6;--high:#c0392b;--mid:#b8860b;--low:#7f8c8d;--got:#e8f5e9;--gotink:#2e7d32;--btn:#2d6cdf;--btnink:#fff;--accent:#2d6cdf;--warnbg:#fdecea;}
  @media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#1f2125;--ink:#e9e9ec;--sub:#9aa0a6;--line:#33353b;--high:#ff6b5e;--mid:#e0b34d;--low:#a4adb3;--got:#1c3a24;--gotink:#7fd694;--btn:#4a86ff;--accent:#4a86ff;--warnbg:#3a1f1c;}}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR",sans-serif;background:var(--bg);color:var(--ink)}
  .wrap{width:100%;max-width:1680px;margin:0 auto;padding:20px 14px 56px}
  h1{font-size:22px;margin:0 0 4px}
  h2.sec{font-size:13px;color:var(--sub);margin:22px 0 8px;font-weight:700;text-transform:uppercase;letter-spacing:.03em}
  .meta{color:var(--sub);font-size:13px;margin-bottom:18px}
  .stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:8px}
  .stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:92px}
  .stat b{display:block;font-size:20px}.stat span{font-size:12px;color:var(--sub)}
  .stat.click{cursor:pointer}.stat.click:hover{border-color:var(--accent)}
  .stat.alert{border-color:var(--high)}.stat.alert b{color:var(--high)}
  .stat.active{border-color:var(--accent);border-width:2px}
  .scope-label{font-size:12px;color:var(--sub);margin:2px 0 8px}
  .cats{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
  .cat{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:6px 12px;font-size:12px;cursor:pointer;white-space:nowrap}
  .cat b{margin-right:5px}
  .cat.active{border-color:var(--accent);background:var(--accent);color:#fff}
  .bar{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
  .bar input{flex:1;min-width:180px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
  .bar button{padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);cursor:pointer}
  .bar button.active{border-color:var(--accent);background:var(--accent);color:#fff}
  .tablewrap{overflow-x:hidden;background:var(--card);border:1px solid var(--line);border-radius:12px}
  table{border-collapse:collapse;width:100%;table-layout:fixed}
  th,td{padding:8px 6px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}
  th{font-size:11px;line-height:1.25;color:var(--sub);font-weight:600;position:sticky;top:0;background:var(--card)}
  th:nth-child(1){width:4%}th:nth-child(2){width:8%}th:nth-child(3){width:14%}th:nth-child(4){width:10%}
  th:nth-child(5){width:12%}th:nth-child(6){width:6%}th:nth-child(7){width:8%}th:nth-child(8){width:15%}th:nth-child(9){width:23%}
  .author-sort{width:100%;padding:0;border:0;background:none;color:inherit;font:inherit;font-weight:inherit;text-align:left;cursor:pointer}
  .author-sort:hover,.author-sort:focus-visible{color:var(--accent)}
  .author-cell{font-size:12px;font-weight:600}
  tr.got{background:var(--got)}tr.got td.title{color:var(--gotink)}
  tr.held{background:color-mix(in srgb,var(--card) 82%,var(--line));color:var(--sub)}
  tr.held td{opacity:.72}tr.held .held-badge,tr.held .held-path{opacity:1}
  .held-badge{display:inline-block;margin-left:6px;padding:1px 7px;border:1px solid var(--gotink);border-radius:10px;color:var(--gotink);font-size:10px;font-weight:700;white-space:nowrap;vertical-align:1px}
  .held-path{font-size:10px;line-height:1.35;color:var(--sub);font-family:ui-monospace,Menlo,monospace;overflow-wrap:anywhere}
  tr.unavailable{box-shadow:inset 4px 0 0 var(--high)}
  .unavailable-badge{display:inline-block;margin-left:6px;padding:1px 7px;border:1px solid var(--high);border-radius:10px;background:var(--warnbg);color:var(--high);font-size:10px;font-weight:700;white-space:nowrap;vertical-align:1px}
  .pri{font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;white-space:nowrap;color:#fff;cursor:pointer;border:none}
  .pri.high{background:var(--high)}.pri.mid{background:var(--mid)}.pri.low{background:var(--low)}
  .pri-wrap{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
  .revert{font-size:10px;color:var(--accent);cursor:pointer;text-decoration:underline;background:none;border:none;padding:0}
  .conf{font-size:10px;font-weight:700;padding:1px 6px;border-radius:5px;margin-left:6px;border:1px solid var(--line)}
  .confA{background:#e8f5e9;color:#2e7d32}.confB{background:#fff8e1;color:#b8860b}.confC{background:#fdecea;color:#c0392b}
  @media (prefers-color-scheme:dark){.confA{background:#1c3a24;color:#7fd694}.confB{background:#3a3416;color:#e0b34d}.confC{background:#3a1f1c;color:#ff6b5e}}
  .title{font-weight:600;font-size:13px;line-height:1.38}.cite{font-size:11px;color:var(--sub)}
  .ref{font-size:10px;color:var(--sub);font-family:ui-monospace,Menlo,monospace}
  a.acc{display:inline-block;padding:4px 7px;background:var(--btn);color:var(--btnink);border-radius:7px;text-decoration:none;font-size:11px;white-space:nowrap}
  .chk{width:18px;height:18px;cursor:pointer}
  .note{font-size:11px;margin-top:3px}.note.warn{color:var(--high)}.note.info{color:var(--sub)}
  .panel{min-width:0}
  .panel textarea{display:block;width:100%;max-width:100%;height:42px;font-size:10px;padding:5px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink);resize:vertical}
  .panel .row{display:flex;gap:4px;margin-bottom:4px;flex-wrap:wrap}
  .mbtn{font-size:9px;padding:3px 5px;border-radius:6px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
  .mbtn.on-req{background:var(--high);color:#fff;border-color:var(--high)}
  .mbtn.on-prio{background:var(--gotink);color:#fff;border-color:var(--gotink)}
  .mbtn.on-skip{background:var(--sub);color:#fff}
  .mbtn.on-unavailable{background:var(--high);color:#fff;border-color:var(--high)}
  .mbtn.on-restype{background:var(--accent);color:#fff;border-color:var(--accent)}
  .mbtn.cite-copy{margin-left:6px;vertical-align:middle}
  .pend{font-size:10px;color:var(--high);margin-top:2px}
  .ack{font-size:10px;color:var(--sub);display:flex;gap:4px;align-items:center;margin-top:3px}
  footer{margin-top:18px;color:var(--sub);font-size:12px}
  @media (max-width:1100px) and (min-width:721px){
    .wrap{padding-left:8px;padding-right:8px}
    th,td{padding:7px 4px}
    .pri{font-size:9px;padding:2px 5px}
    .conf{margin-left:3px}
    .title{font-size:12px}.cite{font-size:10px}
  }
  @media (max-width:720px){
    body{font-size:14px;line-height:1.45}
    .wrap{padding:14px 10px 40px}
    h1{font-size:19px}.meta{font-size:11px;margin-bottom:12px}
    h2.sec{margin-top:16px}
    .stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
    .stat{min-width:0;padding:7px 5px;text-align:center;border-radius:8px}
    .stat b{font-size:17px}.stat span{font-size:9px;line-height:1.2;display:block}
    .cats{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px;gap:6px;margin-bottom:12px}
    .cat{padding:5px 9px;font-size:10px}
    .bar{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
    .bar input{grid-column:1/-1;width:100%;min-width:0}
    .bar button{padding:7px 3px;font-size:11px}
    .bar .refresh{grid-column:1/-1}
    .tablewrap{overflow:visible;background:transparent;border:0;border-radius:0}
    table,tbody{display:block;width:100%}
    thead{display:none}
    tr{display:block;margin-bottom:10px;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
    tr.got{background:var(--got)}
    tr.held{background:color-mix(in srgb,var(--card) 82%,var(--line))}
    td{display:grid;grid-template-columns:82px minmax(0,1fr);gap:8px;width:100%;padding:8px 10px;border-bottom:1px solid var(--line);font-size:12px}
    td:last-child{border-bottom:0}
    td::before{font-size:10px;font-weight:700;color:var(--sub);line-height:1.4;padding-top:2px}
    td:nth-child(1)::before{content:"받음"}
    td:nth-child(2)::before{content:"우선순위"}
    td:nth-child(3)::before{content:"자료"}
    td:nth-child(4)::before{content:"저자"}
    td:nth-child(5)::before{content:"저널·시리즈"}
    td:nth-child(6)::before{content:"접근"}
    td:nth-child(7)::before{content:"원본 위치"}
    td:nth-child(8)::before{content:"재검토"}
    td:nth-child(9)::before{content:"코멘트"}
    .title{font-size:13px}.cite{font-size:11px}
    .panel textarea{height:52px;font-size:12px}
    .mbtn{font-size:10px;padding:5px 7px}
    footer{font-size:10px}
  }
</style></head><body><div class="wrap">
  <h1>📥 Judges 자료 다운로드 대장</h1>
  <div class="meta">Track 1 (미보유 확정) · 정본 <code>worklist/download_queue.csv</code> 자동생성</div>
  <div class="stats" id="stats"></div>
  <div class="scope-label" id="scopeLabel"></div>
  <div class="stats" id="catstats"></div>
  <h2 class="sec">카테고리</h2>
  <div class="cats" id="cats"></div>
  <h2 class="sec">자료 종류</h2>
  <div class="cats" id="types"></div>
  <div class="bar">
    <input id="q" placeholder="검색 (저자·제목·저널)…" oninput="render()">
    <button id="fAll" onclick="setStatus({type:'all'})">전체</button>
    <button id="fMajor" onclick="setStatus({type:'bd',value:'통독'})">Major</button>
    <button id="fSecondary" onclick="setStatus({type:'bd',value:'표적'})">Secondary</button>
    <button id="fTodo" onclick="setStatus({type:'todo'})">미수령만</button>
    <button class="refresh" onclick="location.reload()" title="최신 데이터 다시 불러오기">↻ 새로고침</button>
  </div>
  <div class="tablewrap"><table><thead><tr>
    <th>받음</th><th>우선(클릭:전환)</th><th>자료</th><th id="authorHead" aria-sort="none"><button class="author-sort" type="button" onclick="toggleAuthorSort()">저자 <span id="authorSortMark">⇅</span></button></th><th>저널·시리즈</th><th>접근</th><th>원본 엑셀 위치</th><th>재검토 신청</th><th>코멘트</th>
  </tr></thead><tbody id="rows"></tbody></table></div>
  <footer>
    ✔ <b>받음</b> 체크와 확보불가·재검토·코멘트·우선순위 변경은 이 브라우저에 자동 저장됩니다(localStorage)<span id="syncNote"></span>.<br>
    원본 엑셀 위치 = 기존 <code>Judges_missing_by_character.xlsx</code>의 <b>시트!행</b> 좌표.<br>
    우선순위 배지 <span class="pri high">Major</span><span class="pri mid">Secondary</span><span class="pri low">off-list</span>(클릭하면 다음 값으로 전환, 변경분은 매일 지정 시각 순찰에서 기록) · 신뢰등급 <span class="conf confA">A</span>직접확인 <span class="conf confB">B</span>요약기반 <span class="conf confC">C</span>추정(원문확인) · <b>⚠</b>확인필요 <b>ℹ</b>참고<br>
    <b>재검토 신청</b>: 분류가 틀렸다고 판단되면 코멘트와 함께 신청 — 매일 지정 시각에 AI가 검토 후 결과 기록.
    <b>코멘트</b>: [우선 받기]/[불필요] + 코멘트, AI 자동처리 대상 아님(조교 확인용).
  </footer>
</div><script>
/*DATA*/
const SHEETS_ENDPOINT="__SHEETS_ENDPOINT__";
const LBL={"통독":"Major","표적":"Secondary","off-list":"Off-list"};
const BD_PRI_CLASS={"통독":"high","표적":"mid","off-list":"low"};
const BD_CYCLE=["통독","표적","off-list"];
const KEY_GOT="judges_dl_got_v1";
const KEY_BD="judges_dl_bd_override_v1";
const KEY_BD_HIST="judges_dl_bd_history_v1";
const KEY_RECLASS="judges_dl_reclass_v1";
const KEY_PROF="judges_dl_prof_v1";
const KEY_UNAVAILABLE="judges_dl_unavailable_v1";
const KEY_RESTYPE="judges_dl_restype_override_v1";
const RES_TYPES=["저널논문","단행본","북챕터","학위논문","사전·참고자료","기타"];
let got=JSON.parse(localStorage.getItem(KEY_GOT)||"{}");
let bdOverride=JSON.parse(localStorage.getItem(KEY_BD)||"{}");
let bdHistory=JSON.parse(localStorage.getItem(KEY_BD_HIST)||"[]");
let reclass=JSON.parse(localStorage.getItem(KEY_RECLASS)||"{}");
let prof=JSON.parse(localStorage.getItem(KEY_PROF)||"{}");
let unavailable=JSON.parse(localStorage.getItem(KEY_UNAVAILABLE)||"{}");
let restypeOverride=JSON.parse(localStorage.getItem(KEY_RESTYPE)||"{}");
let statusFilter={type:"all"};
let catFilter=null;
let typeFilter=null;
let authorSort=null;
document.getElementById("syncNote").textContent = SHEETS_ENDPOINT ? "" : " (⚠ 서버 미연결 — 이 기기에만 저장됨)";

function syncToBackend(kind,payload){
  if(!SHEETS_ENDPOINT) return;
  fetch(SHEETS_ENDPOINT,{method:"POST",headers:{"Content-Type":"text/plain"},body:JSON.stringify({kind,...payload})}).catch(()=>{});
}
function save(){
  localStorage.setItem(KEY_GOT,JSON.stringify(got));
  localStorage.setItem(KEY_BD,JSON.stringify(bdOverride));
  localStorage.setItem(KEY_BD_HIST,JSON.stringify(bdHistory));
  localStorage.setItem(KEY_RECLASS,JSON.stringify(reclass));
  localStorage.setItem(KEY_PROF,JSON.stringify(prof));
  localStorage.setItem(KEY_UNAVAILABLE,JSON.stringify(unavailable));
  localStorage.setItem(KEY_RESTYPE,JSON.stringify(restypeOverride));
}
function setStatus(f){statusFilter=f;render()}
function toggleAuthorSort(){authorSort=authorSort==="asc"?"desc":"asc";render()}
function toggle(id){got[id]=!got[id];save();syncToBackend("got",{id,got:got[id]});render()}
function toggleUnavailable(id){
  unavailable[id]=!unavailable[id];
  save();syncToBackend("unavailable",{id,field1:String(unavailable[id])});render();
}
function effBd(d){return bdOverride[d.id]||d.bd}
function cycleBd(id,orig){
  const cur=bdOverride[id]||orig;
  const next=BD_CYCLE[(BD_CYCLE.indexOf(cur)+1)%BD_CYCLE.length];
  const entry={id,from:cur,to:next,ts:new Date().toISOString(),reviewed:false};
  bdHistory.push(entry);
  if(next===orig) delete bdOverride[id]; else bdOverride[id]=next;
  save();syncToBackend("priority_change",entry);render();
}
function revertBd(id){
  const cur=bdOverride[id];
  if(cur===undefined) return;
  const entry={id,from:cur,to:"__revert_to_original__",ts:new Date().toISOString(),reviewed:false};
  bdHistory.push(entry);
  delete bdOverride[id];
  save();syncToBackend("priority_change",entry);render();
}
function effRestype(d){return restypeOverride[d.id]||resourceTypeBucket(d.idType)}
function cycleRestype(id,orig){
  const cur=restypeOverride[id]||orig;
  const next=RES_TYPES[(RES_TYPES.indexOf(cur)+1)%RES_TYPES.length];
  if(next===orig) delete restypeOverride[id]; else restypeOverride[id]=next;
  save();syncToBackend("restype_change",{id,from:cur,to:next});render();
}
function revertRestype(id){
  const cur=restypeOverride[id];
  if(cur===undefined) return;
  delete restypeOverride[id];
  save();syncToBackend("restype_change",{id,from:cur,to:"__revert_to_original__"});render();
}
function toggleReclass(id){
  const r=reclass[id]||{open:false,comment:"",status:null};
  r.open=!r.open;reclass[id]=r;save();render();
}
function submitReclass(id){
  const ta=document.getElementById("rc_"+id);
  const comment=(ta&&ta.value||"").trim();
  if(!comment){alert("코멘트를 입력해 주세요.");return;}
  reclass[id]={open:false,comment,status:"pending",ts:new Date().toISOString()};
  save();syncToBackend("reclass",{id,comment,status:"pending"});render();
}
function setProfChoice(id,choice){
  const p=prof[id]||{choice:null,comment:"",ack:false};
  p.choice = p.choice===choice ? null : choice;
  p.ts=new Date().toISOString();
  prof[id]=p;save();syncToBackend("prof",{id,choice:p.choice,comment:p.comment});render();
}
function saveProfComment(id){
  const ta=document.getElementById("pf_"+id);
  const p=prof[id]||{choice:null,comment:"",ack:false};
  p.comment=(ta&&ta.value||"").trim();p.ts=new Date().toISOString();
  prof[id]=p;save();syncToBackend("prof",{id,choice:p.choice,comment:p.comment});render();
}
function ackProf(id){
  const p=prof[id]||{choice:null,comment:"",ack:false};
  p.ack=!p.ack;prof[id]=p;save();render();
}
async function loadFromBackend(){
  if(!SHEETS_ENDPOINT) return;
  try{
    const res=await fetch(SHEETS_ENDPOINT);
    const data=await res.json();
    if(!data.ok||!data.rows) return;
    data.rows.forEach(r=>{
      const kind=r.kind,id=r.id;
      if(!kind||!id) return;
      if(kind==="got"){ got[id]=(String(r.field1)==="true"); }
      else if(kind==="unavailable"){ unavailable[id]=(String(r.field1)==="true"); }
      else if(kind==="priority_change"){
        if(r.field2==="__revert_to_original__") delete bdOverride[id]; else bdOverride[id]=r.field2;
      }
      else if(kind==="restype_change"){
        if(r.field2==="__revert_to_original__") delete restypeOverride[id]; else restypeOverride[id]=r.field2;
      }
      else if(kind==="reclass"){ reclass[id]={open:false,comment:r.field1,status:r.field2,result:r.field3||"",ts:r.ts}; }
      else if(kind==="prof"){
        const prevAck=(prof[id]&&prof[id].ack)||false;
        prof[id]={choice:r.field1||null,comment:r.field2||"",ack:prevAck,ts:r.ts};
      }
    });
    save();render();
  }catch(err){ /* 서버 미도달 시 로컬 상태 유지 */ }
}

function captureFocusedTextarea(){
  const el=document.activeElement;
  if(!el||el.tagName!=="TEXTAREA"||!/^(rc_|pf_)/.test(el.id)) return null;
  return {id:el.id,value:el.value,selectionStart:el.selectionStart,selectionEnd:el.selectionEnd};
}
function restoreFocusedTextarea(snapshot){
  if(!snapshot) return;
  const el=document.getElementById(snapshot.id);
  if(!el) return;
  el.value=snapshot.value;
  el.focus({preventScroll:true});
  if(snapshot.selectionStart!==null&&snapshot.selectionEnd!==null){
    el.setSelectionRange(snapshot.selectionStart,snapshot.selectionEnd);
  }
}

function isKoreanText(s){
  if(!s) return false;
  const hangul=(s.match(/[가-힣]/g)||[]).length;
  return hangul/s.length>=0.05;
}
function authorSurnames(auRaw){
  if(!auRaw) return [];
  const cleaned=auRaw.replace(/\(eds?\.?\)/gi,"").trim();
  const parts=cleaned.split(/;| and | & /i).map(p=>p.trim()).filter(Boolean);
  return parts.map(p=>{
    if(p.includes(",")) return p.split(",")[0].trim();
    const toks=p.split(/\s+/);
    return toks[toks.length-1];
  });
}
function formatAuthors(auRaw,kr){
  const s=authorSurnames(auRaw);
  if(s.length===0) return kr?"[저자미확인]":"[Author unknown]";
  if(s.length===1) return s[0];
  if(s.length===2) return kr?`${s[0]}, ${s[1]}`:`${s[0]} and ${s[1]}`;
  if(s.length===3) return `${s[0]}, ${s[1]}, ${s[2]}`;
  return kr?`${s[0]} 등`:`${s[0]} et al.`;
}
const STOPWORDS=new Set(["a","an","the","of","in","on","to","for","with","and","or","but","by","from","at","as","into","onto","within","without","between","among","under","over","about","after","before","during","is","are","en","de","du","des","la","le","les","van","von","der","und"]);
function shortTitle(ti){
  if(!ti) return "";
  const prefix=ti.split(":")[0].trim();
  const kr=isKoreanText(prefix);
  if(kr) return prefix;
  let words=prefix.split(/\s+/);
  if(/^(A|An|The)$/i.test(words[0])) words=words.slice(1);
  const contentCount=words.filter(w=>!STOPWORDS.has(w.toLowerCase())).length;
  if(contentCount<=5) return words.join(" ");
  let seen=0,cut=words.length;
  for(let i=0;i<words.length;i++){
    if(!STOPWORDS.has(words[i].toLowerCase())) seen++;
    if(seen===5){ cut=i+1; break; }
  }
  return words.slice(0,cut).join(" ");
}
function buildCitation(d){
  const kr=isKoreanText(d.ti)||isKoreanText(d.au);
  const author=formatAuthors(d.au,kr);
  const ti=shortTitle(d.ti);
  const base=`${author} ${d.yr} ${ti}`;
  const idt=(d.idType||"").toLowerCase();
  const isJournal=/article|journal/.test(idt);
  const isChapter=/chapter/.test(idt);
  const pageLike=/^[0-9]+[–-][0-9]+$/.test((d.identifier||"").trim());
  if(isJournal&&d.jsCite){
    let extra=d.jsCite;
    if(pageLike) extra+=`, ${d.identifier.trim()}`;
    return `${base}_${extra}`;
  }
  if(isChapter&&d.jsCite){
    let extra=d.jsCite;
    if(pageLike) extra+=`. ${d.identifier.trim()}`;
    return `${base}_${extra}`;
  }
  return base;
}
function copyCitation(id){
  const d=DATA.find(x=>x.id===id);
  if(!d) return;
  const text=buildCitation(d);
  const btn=document.getElementById("cite_"+id);
  const done=()=>{ if(btn){ const orig=btn.textContent; btn.textContent="복사됨"; setTimeout(()=>{btn.textContent=orig;},1200);} };
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done).catch(()=>{ prompt("파일명 복사(Ctrl/Cmd+C):",text); });
  }else{
    prompt("파일명 복사(Ctrl/Cmd+C):",text);
  }
}

function resourceTypeBucket(idType){
  const t=(idType||"").toLowerCase().trim();
  if(["journal-ref","article","journal-article","ref-article","review"].includes(t)) return "저널논문";
  if(["book","isbn"].includes(t)) return "단행본";
  if(["book-chapter","book chapter","chapter"].includes(t)) return "북챕터";
  if(["dissertation","thesis"].includes(t)) return "학위논문";
  if(["dictionary entry","dictionary-entry","dictionary","dictionary-article"].includes(t)) return "사전·참고자료";
  return "기타";
}
function render(){
  const focusedTextarea=captureFocusedTextarea();
  const q=(document.getElementById("q").value||"").toLowerCase();
  const authorHead=document.getElementById("authorHead");
  document.getElementById("authorSortMark").textContent=authorSort==="asc"?"▲":authorSort==="desc"?"▼":"⇅";
  authorHead.setAttribute("aria-sort",authorSort==="asc"?"ascending":authorSort==="desc"?"descending":"none");
  ["fAll","fMajor","fSecondary","fTodo"].forEach(x=>document.getElementById(x).classList.remove("active"));
  if(statusFilter.type==="all")document.getElementById("fAll").classList.add("active");
  if(statusFilter.type==="bd"&&statusFilter.value==="통독")document.getElementById("fMajor").classList.add("active");
  if(statusFilter.type==="bd"&&statusFilter.value==="표적")document.getElementById("fSecondary").classList.add("active");
  if(statusFilter.type==="todo")document.getElementById("fTodo").classList.add("active");

  const rows=document.getElementById("rows");rows.innerHTML="";
  const visible=DATA.filter(d=>{
    const bd=effBd(d);
    if(catFilter&&d.cat!==catFilter)return false;
    if(typeFilter&&effRestype(d)!==typeFilter)return false;
    if(statusFilter.type==="bd"&&bd!==statusFilter.value)return false;
    if(statusFilter.type==="todo"&&(got[d.id]||unavailable[d.id]||d.status==="HELD_ALREADY"))return false;
    if(statusFilter.type==="held"&&d.status!=="HELD_ALREADY")return false;
    if(statusFilter.type==="unavailable"&&!unavailable[d.id])return false;
    if(statusFilter.type==="reclass"&&!(reclass[d.id]&&reclass[d.id].status==="pending"))return false;
    if(statusFilter.type==="prof"&&!(prof[d.id]&&(prof[d.id].comment||prof[d.id].choice)&&!prof[d.id].ack))return false;
    if(statusFilter.type==="got"&&!got[d.id])return false;
    if(statusFilter.type==="conf"&&d.conf!==statusFilter.value)return false;
    if(q&&!(d.au+d.ti+d.js).toLowerCase().includes(q))return false;
    return true;
  });
  if(authorSort){
    const direction=authorSort==="asc"?1:-1;
    visible.sort((a,b)=>direction*a.au.localeCompare(b.au,undefined,{sensitivity:"base",numeric:true}));
  }
  visible.forEach(d=>{
    const bd=effBd(d);
    const tr=document.createElement("tr");
    if(got[d.id])tr.classList.add("got");
    if(d.status==="HELD_ALREADY")tr.classList.add("held");
    if(unavailable[d.id])tr.classList.add("unavailable");
    const overridden=bdOverride[d.id]!==undefined;
    const rc=reclass[d.id]||{};
    const pf=prof[d.id]||{};
    const origType=resourceTypeBucket(d.idType);
    const curType=effRestype(d);
    const rtOverridden=restypeOverride[d.id]!==undefined;
    tr.innerHTML=`<td><input type="checkbox" class="chk" ${got[d.id]?"checked":""} onchange="toggle('${d.id}')"></td>
      <td><div class="pri-wrap"><button class="pri ${BD_PRI_CLASS[bd]||d.pri}" onclick="cycleBd('${d.id}','${d.bd}')">${LBL[bd]||bd}</button>${overridden?`<button class="revert" onclick="revertBd('${d.id}')">복원</button>`:""}</div></td>
      <td><div class="title">${d.ti}<span class="conf conf${d.conf}">${d.conf}</span>${d.status==='HELD_ALREADY'?`<span class="held-badge">확보완료</span>`:""}${unavailable[d.id]?`<span class="unavailable-badge">확보불가</span>`:""}</div><div class="cite">${d.yr} <button class="mbtn cite-copy" id="cite_${d.id}" onclick="copyCitation('${d.id}')" title="파일명 규칙으로 복사">📋 파일명</button></div>${d.warn?`<div class="note warn">⚠ ${d.warn}</div>`:""}${d.info?`<div class="note info">ℹ ${d.info}</div>`:""}</td>
      <td class="author-cell">${d.au}</td>
      <td class="cite">${d.js}<div class="row" style="margin-top:5px"><button class="mbtn ${rtOverridden?'on-restype':''}" onclick="cycleRestype('${d.id}','${origType}')" title="클릭할 때마다 다음 자료종류로 전환">📚 ${curType}</button>${rtOverridden?`<button class="revert" onclick="revertRestype('${d.id}')">복원</button>`:""}</div></td>
      <td>${d.status==='HELD_ALREADY'?`<div class="held-path" title="원본 폴더 경로">${d.heldPath||'경로 확인 필요'}</div>`:`<a class="acc" href="${d.link}" target="_blank" rel="noopener">열기 ↗</a>`}</td>
      <td class="ref">${d.ref}</td>
      <td class="panel">
        <button class="mbtn ${unavailable[d.id]?'on-unavailable':''}" onclick="toggleUnavailable('${d.id}')">${unavailable[d.id]?'✕ 확보불가':'확보불가'}</button>
        <button class="mbtn ${rc.status==='pending'?'on-req':''}" onclick="toggleReclass('${d.id}')">${rc.status==='pending'?'대기중':(rc.status==='ai_reviewed'?'검토완료':'재검토 신청')}</button>
        ${rc.status==='pending'?`<div class="pend">⏳ AI 검토 대기</div>`:""}
        ${rc.status==='ai_reviewed'&&rc.result?`<div class="note info">🤖 ${rc.result}</div>`:""}
        ${rc.open?`<div class="row" style="margin-top:5px"><textarea id="rc_${d.id}" placeholder="틀린 이유·근거...">${rc.comment||""}</textarea></div><div class="row"><button class="mbtn" onclick="submitReclass('${d.id}')">신청</button></div>`:""}
      </td>
      <td class="panel">
        <div class="row">
          <button class="mbtn ${pf.choice==='prio'?'on-prio':''}" onclick="setProfChoice('${d.id}','prio')">우선 받기</button>
          <button class="mbtn ${pf.choice==='skip'?'on-skip':''}" onclick="setProfChoice('${d.id}','skip')">불필요</button>
        </div>
        <textarea id="pf_${d.id}" placeholder="코멘트..." onblur="saveProfComment('${d.id}')">${pf.comment||""}</textarea>
        ${(pf.comment||pf.choice)?`<div class="ack"><input type="checkbox" ${pf.ack?"checked":""} onchange="ackProf('${d.id}')"> 확인함</div>`:""}
      </td>`;
    rows.appendChild(tr);
  });
  restoreFocusedTextarea(focusedTextarea);

  const shown=visible.length;
  const total=DATA.length,done=DATA.filter(d=>got[d.id]).length;
  const held=DATA.filter(d=>d.status==="HELD_ALREADY").length;
  const unavailableCount=DATA.filter(d=>unavailable[d.id]).length;
  const todo=DATA.filter(d=>!got[d.id]&&!unavailable[d.id]&&d.status!=="HELD_ALREADY").length;
  const reclassPending=Object.keys(reclass).filter(id=>reclass[id].status==="pending").length;
  const profUnread=Object.keys(prof).filter(id=>{const p=prof[id];return (p.comment||p.choice)&&!p.ack;}).length;
  const statDefs=[
    {type:"all",label:"총 자료",n:total},
    {type:"got",label:"받음 ✔",n:done},
    {type:"todo",label:"미수령",n:todo},
    {type:"held",label:"확보완료",n:held},
    {type:"unavailable",label:"확보불가",n:unavailableCount},
    {type:"bd",value:"통독",label:"Major",n:DATA.filter(d=>effBd(d)==="통독").length},
    {type:"conf",value:"C",label:"C(확인요)",n:DATA.filter(d=>d.conf==="C").length},
    {type:"reclass",label:"재검토 대기",n:reclassPending,alert:!!reclassPending},
    {type:"prof",label:"코멘트 미확인",n:profUnread,alert:!!profUnread},
  ];
  document.getElementById("stats").innerHTML=statDefs.map((s,i)=>{
    const isActive=statusFilter.type===s.type&&(s.value===undefined||statusFilter.value===s.value);
    return `<div class="stat click ${s.alert?'alert':''} ${isActive?'active':''}" data-si="${i}"><b>${s.n}</b><span>${s.label}</span></div>`;
  }).join("") + `<div class="stat"><b>${shown}</b><span>표시중</span></div>`;
  [...document.getElementById("stats").children].slice(0,statDefs.length).forEach((el,i)=>{
    const s=statDefs[i];
    el.onclick=()=>setStatus(s.value!==undefined?{type:s.type,value:s.value}:{type:s.type});
  });

  // 선택된 카테고리·자료종류 범위 안에서의 상태별 세부 현황(상태 필터와 독립적으로 항상 전체 상태를 보여줌 — 카테고리+상태 동시 적용 가능)
  const scoped=DATA.filter(d=>(!catFilter||d.cat===catFilter)&&(!typeFilter||effRestype(d)===typeFilter));
  const sTotal=scoped.length;
  const sDone=scoped.filter(d=>got[d.id]).length;
  const sHeld=scoped.filter(d=>d.status==="HELD_ALREADY").length;
  const sUnavail=scoped.filter(d=>unavailable[d.id]).length;
  const sTodo=scoped.filter(d=>!got[d.id]&&!unavailable[d.id]&&d.status!=="HELD_ALREADY").length;
  const sReclass=scoped.filter(d=>reclass[d.id]&&reclass[d.id].status==="pending").length;
  const scopeStatDefs=[
    {type:"all",label:"범위 전체",n:sTotal},
    {type:"got",label:"받음 ✔",n:sDone},
    {type:"todo",label:"미수령",n:sTodo},
    {type:"held",label:"확보완료",n:sHeld},
    {type:"unavailable",label:"확보불가",n:sUnavail},
    {type:"reclass",label:"재검토 대기",n:sReclass,alert:!!sReclass},
  ];
  const scopeParts=[];
  if(catFilter)scopeParts.push(catFilter);
  if(typeFilter)scopeParts.push(typeFilter);
  document.getElementById("scopeLabel").textContent=`현재 범위: ${scopeParts.length?scopeParts.join(" · "):"전체"} (${sTotal}건) — 아래 배지를 눌러 이 범위 안에서 상태로 다시 좁힐 수 있습니다`;
  document.getElementById("catstats").innerHTML=scopeStatDefs.map((s,i)=>{
    const isActive=statusFilter.type===s.type&&(s.value===undefined||statusFilter.value===s.value);
    return `<div class="stat click ${s.alert?'alert':''} ${isActive?'active':''}" data-si="${i}"><b>${s.n}</b><span>${s.label}</span></div>`;
  }).join("");
  [...document.getElementById("catstats").children].forEach((el,i)=>{
    const s=scopeStatDefs[i];
    el.onclick=()=>setStatus(s.value!==undefined?{type:s.type,value:s.value}:{type:s.type});
  });

  const catCounts={};
  DATA.forEach(d=>{if(d.cat)catCounts[d.cat]=(catCounts[d.cat]||0)+1;});
  const cats=Object.keys(catCounts).sort((a,b)=>catCounts[b]-catCounts[a]);
  const catsEl=document.getElementById("cats");
  catsEl.innerHTML = cats.map((c,i)=>
    `<div class="cat ${catFilter===c?'active':''}" data-idx="${i}"><b>${catCounts[c]}</b>${c}</div>`
  ).join("");
  [...catsEl.children].forEach((el,i)=>{
    el.onclick=()=>{catFilter=(catFilter===cats[i])?null:cats[i];render();};
  });

  const typeCounts={};
  DATA.forEach(d=>{const b=effRestype(d);typeCounts[b]=(typeCounts[b]||0)+1;});
  const types=Object.keys(typeCounts).sort((a,b)=>typeCounts[b]-typeCounts[a]);
  const typesEl=document.getElementById("types");
  typesEl.innerHTML = types.map((t,i)=>
    `<div class="cat ${typeFilter===t?'active':''}" data-idx="${i}"><b>${typeCounts[t]}</b>${t}</div>`
  ).join("");
  [...typesEl.children].forEach((el,i)=>{
    el.onclick=()=>{typeFilter=(typeFilter===types[i])?null:types[i];render();};
  });
}
render();
loadFromBackend();
if(SHEETS_ENDPOINT) setInterval(loadFromBackend,20000);
</script></body></html>"""

html = TEMPLATE.replace("/*DATA*/", "const DATA=" + DATA + ";").replace("__SHEETS_ENDPOINT__", SHEETS_ENDPOINT)
for out in (OUT, os.path.join(HERE, "index.html")):  # index.html = GitHub Pages 진입점
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
print(f"OK: {len(rows)} rows -> download_dashboard.html + index.html")
