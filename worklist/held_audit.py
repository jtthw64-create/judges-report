#!/usr/bin/env python3
# 확보완료(HELD_ALREADY) 누락 재점검: download_queue.csv 전체 QUEUED 항목 vs 원본폴더 604파일
import csv, re, os, unicodedata

BASE = "/Users/nurikim/Library/CloudStorage/GoogleDrive-jtthw64@gmail.com/내 드라이브/Claude Cowork GD"
CSV_PATH = f"{BASE}/judges report/worklist/download_queue.csv"
ORIG_ROOT = f"{BASE}/5 Book 3 Judges Resources"

STOPWORDS = {"judges","judg","book","study","studies","the","and","from","with","essay","essays",
             "vol","article","pdf","epub","in","of","on","a","an","to","for","is","as"}

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def tokens(s):
    return set(re.findall(r"[a-z]{4,}", norm(s))) - STOPWORDS

def letters_only(s):
    # 아포스트로피(Na'aman)·하이픈(Niesiołowski-Spanò)·NFKD로 분해 안 되는 확장 라틴 문자
    # (ł, đ 등)까지 포함해 성(姓)과 파일명을 "글자만 이어붙인 문자열"로 동일하게 정규화한다.
    # 예전 버전은 [A-Za-zÀ-ÿ'-] 문자클래스가 Latin-1 범위 밖 문자(ł 등)를 통째로 버려
    # Na'aman/Niesiołowski처럼 아포스트로피·확장 라틴 문자가 있는 성을 매칭하지 못했다.
    return re.sub(r"[^a-z]", "", norm(s))

def surnames(author_field):
    # split on common separators, take first token of each chunk as surname candidate
    parts = re.split(r"[,&;]| and | und ", author_field)
    names = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        first_word = re.split(r"[\s\(]", p)[0]
        cleaned = letters_only(first_word)
        if len(cleaned) >= 3:
            names.append(cleaned)
    return names

# gather all original files
files = []
for dirpath, _, filenames in os.walk(ORIG_ROOT, followlinks=True):
    for fn in filenames:
        if fn.lower().endswith((".pdf",".epub",".docx",".doc")):
            rel = os.path.relpath(os.path.join(dirpath, fn), ORIG_ROOT)
            files.append((rel, fn))

print(f"원본 파일 수: {len(files)}")

rows = []
with open(CSV_PATH, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"CSV 행 수: {len(rows)}")

queued = [r for r in rows if r["status"] == "QUEUED"]
print(f"QUEUED 행 수: {len(queued)}")

candidates = []
for r in queued:
    year = re.search(r"\d{4}", r["year"] or "")
    year = year.group(0) if year else None
    snames = surnames(r["author"] or "")
    if not year or not snames:
        continue
    tset = tokens(r["title"] or "")
    for rel, fn in files:
        fn_norm = norm(fn)
        if year not in fn_norm:
            continue
        # 부분문자열 매칭: 성에 아포스트로피·하이픈·확장 라틴 문자가 있어도
        # 파일명 쪽 글자만 이어붙인 문자열에 포함되는지로 판단(단어경계 의존 안 함)
        fn_letters = letters_only(fn)
        if not any(sn in fn_letters for sn in snames):
            continue
        ftoks = tokens(fn)
        score = len(tset & ftoks)
        candidates.append((r["id"], r["author"], r["year"], r["title"][:70], rel, score))

print(f"\n후보 매치 수: {len(candidates)}")
candidates.sort(key=lambda x: -x[5])
for c in candidates:
    print(f"score={c[5]:2d} | {c[0]:12s} | {c[1][:30]:30s} {c[2]:5s} | {c[3]}\n           -> {c[4]}")
