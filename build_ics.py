#!/usr/bin/env python3
import json, datetime, hashlib
from pathlib import Path

def esc(s):
    return (s or "").replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")

rows=json.loads(Path("conferences.json").read_text())
lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//Ortho Deadline Calendar//EN","CALSCALE:GREGORIAN","METHOD:PUBLISH"]
now=datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
for r in rows:
    d=r.get("known_deadline")
    if not d: continue
    uid=hashlib.md5((r.get("id","")+d).encode()).hexdigest()+"@ortho-deadline-calendar"
    start=d.replace("-","")
    dt=datetime.date.fromisoformat(d)+datetime.timedelta(days=1)
    end=dt.strftime("%Y%m%d")
    desc=f"{r.get('deadline_label','Abstract deadline')}\\nSubmission: {r.get('submission_url') or r.get('source_url','')}\\nOfficial source: {r.get('source_url','')}\\nStatus: {r.get('status','')}"
    lines += [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now}",
        f"DTSTART;VALUE=DATE:{start}",
        f"DTEND;VALUE=DATE:{end}",
        f"SUMMARY:{esc('Abstract deadline: ' + r.get('name','Conference'))}",
        f"LOCATION:{esc(r.get('location',''))}",
        f"DESCRIPTION:{esc(desc)}",
        "BEGIN:VALARM",
        "TRIGGER:-P7D",
        "ACTION:DISPLAY",
        f"DESCRIPTION:{esc('7-day reminder: ' + r.get('name','Conference') + ' abstract deadline')}",
        "END:VALARM",
        "END:VEVENT"
    ]
lines.append("END:VCALENDAR")
Path("docs").mkdir(exist_ok=True)
Path("calendar.ics").write_text("\n".join(lines)+"\n")
Path("docs/calendar.ics").write_text("\n".join(lines)+"\n")

