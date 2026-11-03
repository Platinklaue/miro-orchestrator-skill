# Optional add-on: usage tracking with ccusage

**Why:** Claude cannot run `/usage` itself. When the user types `/usage`, the output lands in the
conversation and Claude can read it, but between those readings Claude can only guess. ccusage
turns the guess into a measured estimate.

**What ccusage is:** a free open-source CLI (`npx ccusage`, https://github.com/ryoppippi/ccusage)
that reads Claude Code's local log files and reports tokens and the API-equivalent cost per day and
per 5-hour block. It only reads local files; nothing is uploaded. It does **not** know the plan's
limits, so it cannot say "38%" by itself - `scripts/usage_estimate.py` converts its numbers into a
percentage using the user's last real `/usage` reading.

## Setup (ask the user once; it downloads an npm package)
1. Needs Node.js (`npm --version`). Then `npx --yes ccusage@latest daily` once to download and test.
2. Copy `scripts/usage_estimate.py` next to `board_batch.py` (it uses `BOARD_ROOT` for its
   calibration file).
3. Record "usage tracking: ccusage on" in the Claude Session Settings table (optional row
   `Usage tracking` = `ccusage` / `Off`).

## Use
- **Every time the user shows `/usage`:** run
  `python usage_estimate.py calibrate <session %> --week <week %>`. Each calibration improves the
  cost-per-percent average.
- **Before planning a round, and when a round finishes:** run `python usage_estimate.py`. It prints
  `est_window_pct`, `projected_pct_at_block_end` (if the current pace continues) and `minutes_left`.
- **Decide with it** (rules in `modes-and-sleep.md` → Usage budget): if `est_window_pct` or the
  projection passes the "Usage pause at" setting, do a soft sleep and schedule the wake-up for
  `block_end` plus a few minutes; otherwise start the next round. Say in the report that the number
  is an estimate ("~41% (ccusage estimate)").
- `npx ccusage blocks --active` shows the human-readable view; `npx ccusage daily` the daily totals.

## Limits (tell the user honestly)
- The 5-hour blocks of ccusage start at the hour of the first message; the real window may start a
  few minutes differently, so near a reset the estimate can be off.
- Weekly limits are not modelled; keep using the user's `/usage` week number.
- If the plan or model mix changes, recalibrate.
- Without a calibration the script only reports tokens and cost, not a percentage.
