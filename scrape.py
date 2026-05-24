import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "conferences.json"
OUT = ROOT / "docs" / "conferences.json"

DATE_PATTERNS = [
    r"(?:deadline|due|closes?|submission closes?|accepted through)[^\.\n]{0,90}?((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+20\d{2})",
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2}\s*[–-]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?[a-z]*\s*\d{1,2},?\s+20\d{2})",
    r"(20\d{2}-\d{2}-\d{2})",
]

def fetch_text(url: str) -> str:
    headers = {"User-Agent": "OrthoDeadlineBot/0.1 (+personal research calendar; respectful weekly checks)"}
    r = requests.get(url, timeout=20, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(" ").split())

def extract_candidates(text: str):
    hits = []
    for pat in DATE_PATTERNS:
        hits.extend(re.findall(pat, text, flags=re.I))
    return sorted(set(hits))[:12]

def main():
    conferences = json.loads(DATA.read_text())
    now = datetime.now(timezone.utc).isoformat()
    for c in conferences:
        c["last_checked"] = now
        c["detected_candidates"] = []
        try:
            text = fetch_text(c["source_url"])
            c["source_ok"] = True
            c["detected_candidates"] = extract_candidates(text)
            # Conservative: keep curated known_deadline unless null. Never overwrite with uncertain regex.
            if c.get("known_deadline"):
                c["deadline"] = c["known_deadline"]
            c["status_note"] = "Source reachable; curated deadline retained unless manually reviewed."
        except Exception as e:
            c["source_ok"] = False
            c["status_note"] = f"Source check failed: {type(e).__name__}: {e}"
            if c.get("known_deadline"):
                c["deadline"] = c["known_deadline"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(conferences, indent=2))
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    sys.exit(main())
