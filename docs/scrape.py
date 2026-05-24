#!/usr/bin/env python3
"""
Orthopaedic conference deadline updater.

This is a conservative scraper:
- It fetches official source/submission URLs weekly.
- It searches for date-like text near abstract/submission/deadline terms.
- It only overwrites a known_deadline when it finds a high-confidence future date.
- Otherwise it leaves the curated date alone and marks source_checked_at.
"""
import json, re, sys, urllib.request, datetime
from html.parser import HTMLParser
from pathlib import Path

DATA = Path("conferences.json")
OUT = Path("docs/conferences.json")
TODAY = datetime.date.today()

MONTHS = "jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december"
DATE_PATTERNS = [
    re.compile(rf"\b({MONTHS})\.?\s+([0-3]?\d)(?:st|nd|rd|th)?[,]?\s+(20\d{{2}})\b", re.I),
    re.compile(rf"\b([0-3]?\d)\s+({MONTHS})\.?\s+(20\d{{2}})\b", re.I),
    re.compile(r"\b(20\d{2})[-/](0?[1-9]|1[0-2])[-/]([0-3]?\d)\b"),
    re.compile(r"\b(0?[1-9]|1[0-2])[-/]([0-3]?\d)[-/](20\d{2})\b"),
]
KEYWORDS = re.compile(r"(abstract|submission|deadline|submit|closes|due)", re.I)
MONTH_NUM = {m:i for i, names in enumerate([
["jan","january"],["feb","february"],["mar","march"],["apr","april"],["may"],["jun","june"],
["jul","july"],["aug","august"],["sep","sept","september"],["oct","october"],["nov","november"],["dec","december"]], 1) for m in names}

class Strip(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self, data): self.parts.append(data)
    def text(self): return " ".join(self.parts)

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 ortho-deadline-calendar"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")

def html_to_text(html):
    p=Strip(); p.feed(html); return re.sub(r"\s+"," ",p.text())

def parse_match(m):
    groups = m.groups()
    s = m.group(0)
    try:
        if re.match(r"20\d{2}[-/]", s):
            y,mo,d = map(int, groups)
        elif re.match(r"\d{1,2}[-/]", s):
            mo,d,y = map(int, groups)
        elif groups[0].lower().strip(".") in MONTH_NUM:
            mo = MONTH_NUM[groups[0].lower().strip(".")]; d=int(groups[1]); y=int(groups[2])
        else:
            d=int(groups[0]); mo=MONTH_NUM[groups[1].lower().strip(".")]; y=int(groups[2])
        return datetime.date(y,mo,d)
    except Exception:
        return None

def candidates(text):
    out=[]
    for pat in DATE_PATTERNS:
        for m in pat.finditer(text):
            d=parse_match(m)
            if not d or d < TODAY: continue
            start=max(0,m.start()-140); end=min(len(text),m.end()+140)
            ctx=text[start:end]
            score=0
            if KEYWORDS.search(ctx): score += 3
            if re.search(r"abstract",ctx,re.I): score += 2
            if re.search(r"deadline|due|closes|close",ctx,re.I): score += 2
            if score>=4:
                out.append((score,d.isoformat(),ctx[:260]))
    return sorted(out, reverse=True)

def main():
    rows=json.loads(DATA.read_text())
    for r in rows:
        url = r.get("submission_url") or r.get("source_url")
        r["source_checked_at"] = TODAY.isoformat()
        if not url: continue
        try:
            text=html_to_text(fetch(url))
            found=candidates(text)
            if found:
                best=found[0]
                if best[0] >= 5:
                    r["known_deadline"] = best[1]
                    r["status"] = "auto-detected"
                    r["deadline_label"] = r.get("deadline_label") or "Abstract deadline auto-detected"
                    r["scraper_note"] = best[2]
                else:
                    r["status"] = r.get("status","watch")
                    r["scraper_note"] = "Dates found, but confidence was too low to overwrite curated value."
            else:
                r["scraper_note"] = "No high-confidence future abstract deadline found."
        except Exception as e:
            r["scraper_error"] = str(e)[:200]
    DATA.write_text(json.dumps(rows, indent=2))
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
if __name__ == "__main__":
    main()
