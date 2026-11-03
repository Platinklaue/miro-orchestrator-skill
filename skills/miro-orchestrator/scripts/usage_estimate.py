"""Optional add-on: estimate the 5-hour usage window from local Claude Code logs (via ccusage).

Claude cannot run /usage itself. ccusage (https://github.com/ryoppippi/ccusage, `npx ccusage`) reads the
local Claude Code logs and reports tokens and API-equivalent cost per 5-hour block. It does not know
the plan's limits, so this script converts cost into "% of the window" with a calibration taken from
the user's last real /usage reading.

Usage:
  python usage_estimate.py                      # estimate now (needs one calibration first)
  python usage_estimate.py calibrate 38         # the user's /usage said "Current session: 38% used"
  python usage_estimate.py calibrate 38 --week 45

Calibration file: $BOARD_ROOT/usage_calibration.json (or ./usage_calibration.json without BOARD_ROOT).
Output: one JSON line, e.g.
  {"block_end": "...", "minutes_left": 114, "cost_usd": 103.0, "est_window_pct": 41.2,
   "projected_pct_at_block_end": 66.5, "cost_per_pct": 2.5, "calibrated_at": "...", "note": "estimate"}
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("BOARD_ROOT", "."))
CAL = ROOT / "usage_calibration.json"


def active_block():
    cmd = "npx --yes ccusage@latest blocks --active --json"
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("ccusage failed: " + (out.stderr or "no output")[-300:])
    data = json.loads(out.stdout)
    blocks = data.get("blocks", [])
    if not blocks:
        return None
    return blocks[0]


def main():
    args = sys.argv[1:]
    b = active_block()
    if args[:1] == ["calibrate"]:
        pct = float(args[1])
        if b is None or pct <= 0:
            sys.exit("calibrate: need an active block and a percentage > 0")
        cal = {"window_pct": pct, "block_cost": b["costUSD"], "block_start": b["startTime"],
               "cost_per_pct": b["costUSD"] / pct, "calibrated_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        if "--week" in args:
            cal["week_pct"] = float(args[args.index("--week") + 1])
        old = json.loads(CAL.read_text()) if CAL.exists() else {}
        hist = old.get("history", [])[-19:] + [dict(cal)]
        # Average cost-per-percent over recent calibrations (plans and models stay the same).
        cal["cost_per_pct"] = sum(h["cost_per_pct"] for h in hist) / len(hist)
        cal["history"] = hist
        CAL.write_text(json.dumps(cal, indent=1))
        print(json.dumps({k: v for k, v in cal.items() if k != "history"}))
        return
    if b is None:
        print(json.dumps({"est_window_pct": 0, "note": "no active block (window idle or reset)"}))
        return
    res = {"block_start": b["startTime"], "block_end": b["endTime"],
           "minutes_left": (b.get("projection") or {}).get("remainingMinutes"),
           "cost_usd": round(b["costUSD"], 2),
           "cost_per_hour": round((b.get("burnRate") or {}).get("costPerHour", 0), 2)}
    if CAL.exists():
        cal = json.loads(CAL.read_text())
        cpp = cal["cost_per_pct"]
        res["est_window_pct"] = round(b["costUSD"] / cpp, 1)
        proj = (b.get("projection") or {}).get("totalCost")
        if proj:
            res["projected_pct_at_block_end"] = round(proj / cpp, 1)
        res["cost_per_pct"] = round(cpp, 3)
        res["calibrated_at"] = cal["calibrated_at"]
        res["note"] = "estimate; ccusage blocks may not start exactly when the real window does"
    else:
        res["note"] = "not calibrated: ask the user for /usage once, then run 'calibrate <percent>'"
    print(json.dumps(res))


if __name__ == "__main__":
    main()
