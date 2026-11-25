"""Adds the run record in a "[run]" issue to data/runs.jsonl.

Called by .github/workflows/collect.yml with the issue event. The issue text
is only ever read as data: it is parsed as JSON, checked, cut down to the
fields below, and written as one line.
"""

import json
import os
import re
import sys
from pathlib import Path

DATA = Path("data/runs.jsonl")
KEEP = ("schema", "id", "date", "tool", "machine", "emulator", "settings", "performance", "failures", "note")


HASH16 = re.compile(r"\b[0-9a-f]{16}\b")


def text(v, n=300):
    # Title shader hashes never go in the dataset (VIctory's rule 7, #1633).
    return HASH16.sub("<shader>", str(v))[:n]


def clean(rec):
    if not isinstance(rec, dict) or rec.get("schema") != 1:
        raise ValueError("not a schema 1 run record")
    if not re.fullmatch(r"[0-9a-f]{16}", str(rec.get("id", ""))):
        raise ValueError("bad id")
    out = {k: rec[k] for k in KEEP if k in rec}
    m = out.get("machine") or {}
    out["machine"] = {
        "os": text(m.get("os", "")), "cpu": text(m.get("cpu", "")),
        "gpus": [text(g, 120) for g in (m.get("gpus") or [])[:4]],
        "ram_gb": m.get("ram_gb") if isinstance(m.get("ram_gb"), (int, float)) else None,
    }
    # (The title build's BLAKE3 is a build identity, allowed; it is 64 hex
    # digits, which the shader-hash rule does not touch.)
    out["emulator"] = {text(k, 40): text(v, 160) for k, v in list((out.get("emulator") or {}).items())[:10]}
    out["settings"] = {text(k, 60): text(v, 200) for k, v in list((out.get("settings") or {}).items())[:80]
                       if str(k).startswith("VICTORY_")}
    perf = out.get("performance") or {}
    out["performance"] = {text(k, 30): (v if isinstance(v, (int, float)) else text(v, 20))
                          for k, v in list(perf.items())[:20]}
    out["failures"] = [{"key": text(f.get("key", ""), 200), "count": int(f.get("count", 0)),
                        "status": text(f.get("status", ""), 20)}
                       for f in (out.get("failures") or [])[:20] if isinstance(f, dict)]
    if "note" in out:
        out["note"] = text(out["note"], 500)
    return out


def main():
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    issue = event["issue"]
    if not issue["title"].startswith("[run]"):
        print("not a run report")
        return 0
    body = issue.get("body") or ""
    if len(body) > 40000:
        print("too long")
        return 1
    m = re.search(r"```json\s*(\{.*?\})\s*```", body, re.S)
    if not m:
        print("no JSON block")
        return 1
    rec = clean(json.loads(m.group(1)))
    rec["issue"] = issue["number"]
    rows = DATA.read_text().splitlines() if DATA.exists() else []
    if any(json.loads(r).get("id") == rec["id"] for r in rows if r.strip()):
        print("already there")
        return 0
    DATA.parent.mkdir(exist_ok=True)
    with DATA.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":"), sort_keys=True) + "\n")
    print("added", rec["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
