// Judges 대시보드 백엔드 (Google Apps Script, 바인드형 — 전용 스프레드시트에 연결해서 사용)
// 이벤트로그 방식: 모든 변경을 새 행으로 append. 최신 상태는 마지막 행(kind+id 기준)이 우선.
// 배포: 확장 프로그램 > Apps Script > 이 코드를 붙여넣기 > 배포 > 웹앱
//   실행 계정: 나(소유자) / 액세스 권한: 전체 허용(익명) — URL은 비공개로 유지.

const SHEET_NAME = "events";

function getSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(["ts", "kind", "id", "field1", "field2", "field3"]);
  }
  return sh;
}

function doPost(e) {
  const sheet = getSheet();
  let data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: "bad json" }))
      .setMimeType(ContentService.MimeType.JSON);
  }
  const ts = new Date().toISOString();
  const kind = data.kind || "";
  const id = data.id || "";
  let f1 = "", f2 = "", f3 = "";
  if (kind === "got") {
    f1 = String(data.got);
  } else if (kind === "priority_change") {
    f1 = data.from || ""; f2 = data.to || ""; f3 = data.reviewed ? "reviewed" : "pending";
  } else if (kind === "reclass") {
    f1 = data.comment || ""; f2 = data.status || ""; f3 = data.result || "";
  } else if (kind === "prof") {
    f1 = data.choice || ""; f2 = data.comment || "";
  } else if (kind === "unavailable") {
    f1 = data.field1 || "";
  }
  sheet.appendRow([ts, kind, id, f1, f2, f3]);
  return ContentService.createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  const sheet = getSheet();
  const values = sheet.getDataRange().getValues();
  const headers = values.shift();
  const rows = values.map(r => {
    const o = {};
    headers.forEach((h, i) => (o[h] = r[i]));
    return o;
  });
  return ContentService.createTextOutput(JSON.stringify({ ok: true, rows }))
    .setMimeType(ContentService.MimeType.JSON);
}
