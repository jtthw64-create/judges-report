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
  th:nth-child(1){width:4%}th:nth-child(2){width:8%}th:nth-child(3){width:23%}th:nth-child(4){width:14%}
  th:nth-child(5){width:6%}th:nth-child(6){width:9%}th:nth-child(7){width:15%}th:nth-child(8){width:21%}
  tr.got{background:var(--got)}tr.got td.title{color:var(--gotink)}
  tr.held{background:color-mix(in srgb,var(--card) 82%,var(--line));color:var(--sub)}
  tr.held td{opacity:.72}tr.held .held-badge,tr.held .held-path{opacity:1}
  .held-badge{display:inline-block;margin-left:6px;padding:1px 7px;border:1px solid var(--gotink);border-radius:10px;color:var(--gotink);font-size:10px;font-weight:700;white-space:nowrap;vertical-align:1px}
  .held-path{font-size:10px;line-height:1.35;color:var(--sub);font-family:ui-monospace,Menlo,monospace;overflow-wrap:anywhere}
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
    td:nth-child(4)::before{content:"저널·시리즈"}
    td:nth-child(5)::before{content:"접근"}
    td:nth-child(6)::before{content:"원본 위치"}
    td:nth-child(7)::before{content:"재검토"}
    td:nth-child(8)::before{content:"교수님 코멘트"}
    .title{font-size:13px}.cite{font-size:11px}
    .panel textarea{height:52px;font-size:12px}
    .mbtn{font-size:10px;padding:5px 7px}
    footer{font-size:10px}
  }
</style></head><body><div class="wrap">
  <h1>📥 Judges 자료 다운로드 대장</h1>
  <div class="meta">Track 1 (미보유 확정) · 정본 <code>worklist/download_queue.csv</code> 자동생성</div>
  <div class="stats" id="stats"></div>
  <h2 class="sec">카테고리</h2>
  <div class="cats" id="cats"></div>
  <div class="bar">
    <input id="q" placeholder="검색 (저자·제목·저널)…" oninput="render()">
    <button id="fAll" onclick="setF({type:'all'})">전체</button>
    <button id="fMajor" onclick="setF({type:'bd',value:'통독'})">Major</button>
    <button id="fSecondary" onclick="setF({type:'bd',value:'표적'})">Secondary</button>
    <button id="fTodo" onclick="setF({type:'todo'})">미수령만</button>
    <button class="refresh" onclick="location.reload()" title="최신 데이터 다시 불러오기">↻ 새로고침</button>
  </div>
  <div class="tablewrap"><table><thead><tr>
    <th>받음</th><th>우선(클릭:전환)</th><th>자료</th><th>저널·시리즈</th><th>접근</th><th>원본 엑셀 위치</th><th>재검토 신청</th><th>교수님 코멘트</th>
  </tr></thead><tbody id="rows"></tbody></table></div>
  <footer>
    ✔ <b>받음</b> 체크와 재검토·코멘트·우선순위 변경은 이 브라우저에 자동 저장됩니다(localStorage)<span id="syncNote"></span>.<br>
    원본 엑셀 위치 = 기존 <code>Judges_missing_by_character.xlsx</code>의 <b>시트!행</b> 좌표.<br>
    우선순위 배지 <span class="pri high">Major</span><span class="pri mid">Secondary</span><span class="pri low">off-list</span>(클릭하면 다음 값으로 전환, 변경분은 매일 지정 시각 순찰에서 기록) · 신뢰등급 <span class="conf confA">A</span>직접확인 <span class="conf confB">B</span>요약기반 <span class="conf confC">C</span>추정(원문확인) · <b>⚠</b>확인필요 <b>ℹ</b>참고<br>
    <b>재검토 신청</b>: 분류가 틀렸다고 판단되면 코멘트와 함께 신청 — 매일 지정 시각에 AI가 검토 후 결과 기록.
    <b>교수님 코멘트</b>: [우선 받기]/[불필요] + 코멘트, AI 자동처리 대상 아님(조교 확인용).
  </footer>
</div><script>
/*DATA*/
const SHEETS_ENDPOINT="__SHEETS_ENDPOINT__";
const LBL={"통독":"Major","표적":"Secondary","off-list":"Off-list"};
const BD_CYCLE=["통독","표적","off-list"];
const KEY_GOT="judges_dl_got_v1";
const KEY_BD="judges_dl_bd_override_v1";
const KEY_BD_HIST="judges_dl_bd_history_v1";
const KEY_RECLASS="judges_dl_reclass_v1";
const KEY_PROF="judges_dl_prof_v1";
let got=JSON.parse(localStorage.getItem(KEY_GOT)||"{}");
let bdOverride=JSON.parse(localStorage.getItem(KEY_BD)||"{}");
let bdHistory=JSON.parse(localStorage.getItem(KEY_BD_HIST)||"[]");
let reclass=JSON.parse(localStorage.getItem(KEY_RECLASS)||"{}");
let prof=JSON.parse(localStorage.getItem(KEY_PROF)||"{}");
let filter={type:"all"};
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
}
function setF(f){filter=f;render()}
function toggle(id){got[id]=!got[id];save();syncToBackend("got",{id,got:got[id]});render()}
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
      else if(kind==="priority_change"){
        if(r.field2==="__revert_to_original__") delete bdOverride[id]; else bdOverride[id]=r.field2;
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

function render(){
  const q=(document.getElementById("q").value||"").toLowerCase();
  ["fAll","fMajor","fSecondary","fTodo"].forEach(x=>document.getElementById(x).classList.remove("active"));
  if(filter.type==="all")document.getElementById("fAll").classList.add("active");
  if(filter.type==="bd"&&filter.value==="통독")document.getElementById("fMajor").classList.add("active");
  if(filter.type==="bd"&&filter.value==="표적")document.getElementById("fSecondary").classList.add("active");
  if(filter.type==="todo")document.getElementById("fTodo").classList.add("active");

  const rows=document.getElementById("rows");rows.innerHTML="";let shown=0;
  DATA.forEach(d=>{
    const bd=effBd(d);
    if(filter.type==="bd"&&bd!==filter.value)return;
    if(filter.type==="todo"&&(got[d.id]||d.status==="HELD_ALREADY"))return;
    if(filter.type==="held"&&d.status!=="HELD_ALREADY")return;
    if(filter.type==="category"&&d.cat!==filter.value)return;
    if(filter.type==="reclass"&&!(reclass[d.id]&&reclass[d.id].status==="pending"))return;
    if(filter.type==="prof"&&!(prof[d.id]&&(prof[d.id].comment||prof[d.id].choice)&&!prof[d.id].ack))return;
    if(filter.type==="got"&&!got[d.id])return;
    if(filter.type==="conf"&&d.conf!==filter.value)return;
    if(q&&!(d.au+d.ti+d.js).toLowerCase().includes(q))return;
    shown++;const tr=document.createElement("tr");
    if(got[d.id])tr.classList.add("got");
    if(d.status==="HELD_ALREADY")tr.classList.add("held");
    const overridden=bdOverride[d.id]!==undefined;
    const rc=reclass[d.id]||{};
    const pf=prof[d.id]||{};
    tr.innerHTML=`<td><input type="checkbox" class="chk" ${got[d.id]?"checked":""} onchange="toggle('${d.id}')"></td>
      <td><div class="pri-wrap"><button class="pri ${d.pri}" onclick="cycleBd('${d.id}','${d.bd}')">${LBL[bd]||bd}</button>${overridden?`<button class="revert" onclick="revertBd('${d.id}')">복원</button>`:""}</div></td>
      <td><div class="title">${d.ti}<span class="conf conf${d.conf}">${d.conf}</span>${d.status==='HELD_ALREADY'?`<span class="held-badge">확보완료</span>`:""}</div><div class="cite">${d.au} (${d.yr})</div>${d.warn?`<div class="note warn">⚠ ${d.warn}</div>`:""}${d.info?`<div class="note info">ℹ ${d.info}</div>`:""}</td>
      <td class="cite">${d.js}</td>
      <td>${d.status==='HELD_ALREADY'?`<div class="held-path" title="원본 폴더 경로">${d.heldPath||'경로 확인 필요'}</div>`:`<a class="acc" href="${d.link}" target="_blank" rel="noopener">열기 ↗</a>`}</td>
      <td class="ref">${d.ref}</td>
      <td class="panel">
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

  const total=DATA.length,done=DATA.filter(d=>got[d.id]).length;
  const held=DATA.filter(d=>d.status==="HELD_ALREADY").length;
  const todo=DATA.filter(d=>!got[d.id]&&d.status!=="HELD_ALREADY").length;
  const reclassPending=Object.keys(reclass).filter(id=>reclass[id].status==="pending").length;
  const profUnread=Object.keys(prof).filter(id=>{const p=prof[id];return (p.comment||p.choice)&&!p.ack;}).length;
  const statDefs=[
    {type:"all",label:"총 자료",n:total},
    {type:"got",label:"받음 ✔",n:done},
    {type:"todo",label:"미수령",n:todo},
    {type:"held",label:"확보완료",n:held},
    {type:"bd",value:"통독",label:"Major",n:DATA.filter(d=>effBd(d)==="통독").length},
    {type:"conf",value:"C",label:"C(확인요)",n:DATA.filter(d=>d.conf==="C").length},
    {type:"reclass",label:"재검토 대기",n:reclassPending,alert:!!reclassPending},
    {type:"prof",label:"교수님 미확인",n:profUnread,alert:!!profUnread},
  ];
  document.getElementById("stats").innerHTML=statDefs.map((s,i)=>{
    const isActive=filter.type===s.type&&(s.value===undefined||filter.value===s.value);
    return `<div class="stat click ${s.alert?'alert':''} ${isActive?'active':''}" data-si="${i}"><b>${s.n}</b><span>${s.label}</span></div>`;
  }).join("") + `<div class="stat"><b>${shown}</b><span>표시중</span></div>`;
  [...document.getElementById("stats").children].slice(0,statDefs.length).forEach((el,i)=>{
    const s=statDefs[i];
    el.onclick=()=>setF(s.value!==undefined?{type:s.type,value:s.value}:{type:s.type});
  });

  const catCounts={};
  DATA.forEach(d=>{if(d.cat)catCounts[d.cat]=(catCounts[d.cat]||0)+1;});
  const cats=Object.keys(catCounts).sort((a,b)=>catCounts[b]-catCounts[a]);
  const catsEl=document.getElementById("cats");
  catsEl.innerHTML = cats.map((c,i)=>
    `<div class="cat ${filter.type==='category'&&filter.value===c?'active':''}" data-idx="${i}"><b>${catCounts[c]}</b>${c}</div>`
  ).join("");
  [...catsEl.children].forEach((el,i)=>{
    el.onclick=()=>setF(filter.type==='category'&&filter.value===cats[i] ? {type:'all'} : {type:'category',value:cats[i]});
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
