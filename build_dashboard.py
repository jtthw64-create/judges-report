#!/usr/bin/env python3
# download_queue.csv -> download_dashboard.html 자동 생성
# 사용: (judges report/ 에서) python3 build_dashboard.py
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "worklist", "download_queue.csv")
OUT = os.path.join(HERE, "download_dashboard.html")

WARN_KW = ["정정", "난이도", "미상", "확인요"]

rows = []
with open(CSV, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        conf = (r.get("confidence") or "").strip()
        notes = (r.get("notes") or "").strip()
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
            "id": r["id"], "pri": r["priority"], "bd": r["boundary"], "conf": conf,
            "au": r["author"], "yr": r["year"], "ti": r["title"], "js": js,
            "link": r["access_link"], "ref": r["xlsx_ref"], "warn": warn, "info": info,
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
  :root{--bg:#f7f7f8;--card:#fff;--ink:#1a1a1a;--sub:#666;--line:#e3e3e6;--high:#c0392b;--mid:#b8860b;--low:#7f8c8d;--got:#e8f5e9;--gotink:#2e7d32;--btn:#2d6cdf;--btnink:#fff;}
  @media (prefers-color-scheme:dark){:root{--bg:#16171a;--card:#1f2125;--ink:#e9e9ec;--sub:#9aa0a6;--line:#33353b;--high:#ff6b5e;--mid:#e0b34d;--low:#a4adb3;--got:#1c3a24;--gotink:#7fd694;--btn:#4a86ff;}}
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR",sans-serif;background:var(--bg);color:var(--ink)}
  .wrap{max-width:1100px;margin:0 auto;padding:24px 16px 60px}
  h1{font-size:22px;margin:0 0 4px}
  .meta{color:var(--sub);font-size:13px;margin-bottom:18px}
  .stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px}
  .stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:92px}
  .stat b{display:block;font-size:20px}.stat span{font-size:12px;color:var(--sub)}
  .bar{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
  .bar input{flex:1;min-width:180px;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink)}
  .bar button{padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);cursor:pointer}
  .tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px}
  table{border-collapse:collapse;width:100%;min-width:820px}
  th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
  th{font-size:12px;color:var(--sub);font-weight:600;position:sticky;top:0;background:var(--card)}
  tr.got{background:var(--got)}tr.got td.title{color:var(--gotink)}
  .pri{font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;white-space:nowrap;color:#fff}
  .pri.high{background:var(--high)}.pri.mid{background:var(--mid)}.pri.low{background:var(--low)}
  .conf{font-size:10px;font-weight:700;padding:1px 6px;border-radius:5px;margin-left:6px;border:1px solid var(--line)}
  .confA{background:#e8f5e9;color:#2e7d32}.confB{background:#fff8e1;color:#b8860b}.confC{background:#fdecea;color:#c0392b}
  @media (prefers-color-scheme:dark){.confA{background:#1c3a24;color:#7fd694}.confB{background:#3a3416;color:#e0b34d}.confC{background:#3a1f1c;color:#ff6b5e}}
  .title{font-weight:600;max-width:360px}.cite{font-size:12px;color:var(--sub)}
  .ref{font-size:11px;color:var(--sub);font-family:ui-monospace,Menlo,monospace;white-space:nowrap}
  a.acc{display:inline-block;padding:5px 10px;background:var(--btn);color:var(--btnink);border-radius:7px;text-decoration:none;font-size:12px;white-space:nowrap}
  .chk{width:20px;height:20px;cursor:pointer}
  .note{font-size:11px;margin-top:3px}.note.warn{color:var(--high)}.note.info{color:var(--sub)}
  footer{margin-top:18px;color:var(--sub);font-size:12px}
</style></head><body><div class="wrap">
  <h1>📥 Judges 자료 다운로드 대장</h1>
  <div class="meta">Track 1 (미보유 확정) · 정본 <code>worklist/download_queue.csv</code> 자동생성</div>
  <div class="stats" id="stats"></div>
  <div class="bar">
    <input id="q" placeholder="검색 (저자·제목·저널)…" oninput="render()">
    <button onclick="setF('all')">전체</button><button onclick="setF('통독')">통독</button>
    <button onclick="setF('표적')">표적</button><button onclick="setF('todo')">미수령만</button>
  </div>
  <div class="tablewrap"><table><thead><tr>
    <th>받음</th><th>우선</th><th>자료</th><th>저널·시리즈</th><th>접근</th><th>원본 엑셀 위치</th>
  </tr></thead><tbody id="rows"></tbody></table></div>
  <footer>
    ✔ <b>받음</b> 체크는 이 브라우저에 자동 저장됩니다(localStorage).<br>
    원본 엑셀 위치 = 기존 <code>Judges_missing_by_character.xlsx</code>의 <b>시트!행</b> 좌표.<br>
    우선순위 <span class="pri high">통독</span><span class="pri mid">표적</span><span class="pri low">off-list</span> · 신뢰등급 <span class="conf confA">A</span>직접확인 <span class="conf confB">B</span>요약기반 <span class="conf confC">C</span>추정(원문확인) · <b>⚠</b>확인필요 <b>ℹ</b>참고
  </footer>
</div><script>
/*DATA*/
const KEY="judges_dl_got_v1";
let got=JSON.parse(localStorage.getItem(KEY)||"{}");let filter="all";
function setF(f){filter=f;render()}
function toggle(id){got[id]=!got[id];localStorage.setItem(KEY,JSON.stringify(got));render()}
function render(){
  const q=(document.getElementById("q").value||"").toLowerCase();
  const rows=document.getElementById("rows");rows.innerHTML="";let shown=0;
  DATA.forEach(d=>{
    if(filter==="통독"&&d.bd!=="통독")return;
    if(filter==="표적"&&d.bd!=="표적")return;
    if(filter==="todo"&&got[d.id])return;
    if(q&&!(d.au+d.ti+d.js).toLowerCase().includes(q))return;
    shown++;const tr=document.createElement("tr");if(got[d.id])tr.className="got";
    tr.innerHTML=`<td><input type="checkbox" class="chk" ${got[d.id]?"checked":""} onchange="toggle('${d.id}')"></td>
      <td><span class="pri ${d.pri}">${d.bd}</span></td>
      <td><div class="title">${d.ti}<span class="conf conf${d.conf}">${d.conf}</span></div><div class="cite">${d.au} (${d.yr})</div>${d.warn?`<div class="note warn">⚠ ${d.warn}</div>`:""}${d.info?`<div class="note info">ℹ ${d.info}</div>`:""}</td>
      <td class="cite">${d.js}</td>
      <td><a class="acc" href="${d.link}" target="_blank" rel="noopener">열기 ↗</a></td>
      <td class="ref">${d.ref}</td>`;
    rows.appendChild(tr);
  });
  const total=DATA.length,done=DATA.filter(d=>got[d.id]).length;
  document.getElementById("stats").innerHTML=
    `<div class="stat"><b>${total}</b><span>총 자료</span></div>
     <div class="stat"><b>${done}</b><span>받음 ✔</span></div>
     <div class="stat"><b>${total-done}</b><span>미수령</span></div>
     <div class="stat"><b>${DATA.filter(d=>d.bd==="통독").length}</b><span>통독</span></div>
     <div class="stat"><b>${DATA.filter(d=>d.conf==="C").length}</b><span>C(확인요)</span></div>
     <div class="stat"><b>${shown}</b><span>표시중</span></div>`;
}
render();
</script></body></html>"""

html = TEMPLATE.replace("/*DATA*/", "const DATA=" + DATA + ";")
for out in (OUT, os.path.join(HERE, "index.html")):  # index.html = GitHub Pages 진입점
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
print(f"OK: {len(rows)} rows -> download_dashboard.html + index.html")
