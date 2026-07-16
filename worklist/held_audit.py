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

def surnames(author_field):
    # split on common separators, take first token of each chunk as surname candidate
    parts = re.split(r"[,&;]| and | und ", author_field)
    names = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        first_word = re.split(r"[\s\(]", p)[0]
        first_word = re.sub(r"[^A-Za-zÀ-ÿ'-]", "", first_word)
        if len(first_word) >= 3:
            names.append(norm(first_word))
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
        # word-boundary surname match
        fn_words = set(re.findall(r"[a-z]{3,}", fn_norm))
        if not any(sn in fn_words for sn in snames):
            continue
        ftoks = tokens(fn)
        score = len(tset & ftoks)
        candidates.append((r["id"], r["author"], r["year"], r["title"][:70], rel, score))

print(f"\n후보 매치 수: {len(candidates)}")
candidates.sort(key=lambda x: -x[5])
for c in candidates:
    print(f"score={c[5]:2d} | {c[0]:12s} | {c[1][:30]:30s} {c[2]:5s} | {c[3]}\n           -> {c[4]}")
