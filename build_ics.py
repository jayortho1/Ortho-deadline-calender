import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "conferences.json"
OUT = ROOT / "docs" / "ortho-abstract-deadlines.ics"

def esc(s):
    return str(s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def dtstamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Ortho Deadline Auto//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "X-WR-CALNAME:Orthopaedic Abstract Deadlines",
    "X-WR-TIMEZONE:America/New_York",
]
for c in json.loads(DATA.read_text()):
    date = c.get("deadline") or c.get("known_deadline")
    if not date:
        continue
    ymd = date.replace("-", "")
    desc = "\n".join([
        c.get("deadline_label", "Abstract deadline"),
        "Specialty: " + ", ".join(c.get("specialty", [])),
        "Region: " + c.get("region", ""),
        "Tags: " + ", ".join(c.get("tags", [])),
        "Acceptance strategy: " + c.get("acceptance_strategy", ""),
        "Indexed/publication note: " + c.get("indexed", ""),
        "Source: " + c.get("source_url", ""),
        "Last checked: " + c.get("last_checked", ""),
    ])
    uid = f"{c['id']}-{ymd}@ortho-deadline-auto"
    lines += [
        "BEGIN:VEVENT",
        f"UID:{esc(uid)}",
        f"DTSTAMP:{dtstamp()}",
        f"DTSTART;VALUE=DATE:{ymd}",
        f"SUMMARY:{esc('Abstract deadline: ' + c['name'])}",
        f"DESCRIPTION:{esc(desc)}",
        f"URL:{esc(c.get('source_url',''))}",
    ]
    for days in (30, 14, 7):
        lines += ["BEGIN:VALARM", f"TRIGGER:-P{days}D", "ACTION:DISPLAY", f"DESCRIPTION:{esc(str(days)+' days until abstract deadline')}", "END:VALARM"]
    lines.append("END:VEVENT")
lines.append("END:VCALENDAR")
OUT.write_text("\r\n".join(lines) + "\r\n")
print(f"Wrote {OUT}")
