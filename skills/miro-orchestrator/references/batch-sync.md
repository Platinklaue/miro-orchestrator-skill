# Batched board sync

## Shared board folder (outside the repo, visible to every worktree)
```
<board-root>/            e.g. C:/Users/<you>/<Projects>/.<project>_board/
  config.json            {"kanban_id": "...", "ideas_id": "..."}
  design_table.json      widget + field ids of design, review and status tables; design row ids (D01: <record id>)
  mirror.json            last known kanban rows {record_id: {column: value}} + ideas rows + field ids
  outbox/*.json          pending card changes from workers (one change per file)
  ideas/IDEA-<id>.json   ideas exported for workers
  archive/<stamp>/       consumed outbox and idea files
  SLEEP_STATE.md         the round snapshot (see modes-and-sleep.md)
<claims-root>/           e.g. .<project>_claims/  - atomic mkdir claims and tool slots
```
Set the environment variable `BOARD_ROOT` to this folder before running `scripts/board_batch.py` (it refuses to run without it).

## Outbox file format (workers write these, never Miro)
Name: `<UTC yyyyMMddTHHmmss>-<worker>-<task>-<n>.json`.
```json
{"task": "T38", "set": {"Status": "In progress: working", "Description": "▰▰▰▰▱▱▱▱▱▱ 40% | Done: ... Next: ... [agent/crawl]", "Progress": 40}}
{"task": "T73", "create": {"Title": "T73 Companion remarks", "Status": "Todo: Claude can do", "Milestone": "M8 Polish",
  "Description": "...", "Owner": "Claude", "Ready": "Ready", "Progress": 0, "Session": ""}}
```
Workers write one at start, one around halfway, one at the end. The orchestrator writes its own
`create` files for bugs and todos it finds (`<stamp>-orchestrator-T<nn>-create.json`).

## One sync per round (about 2-4 Miro calls)
1. Read the status table (`table_list_rows`, 1 call) and, if the note or the round needs it, the
   ideas table. Only do a full `canvas_read_as_svg` of kanban + ideas when the mirror may be stale
   (the user edited cards), then `board_batch.py ingest <read.svg>`.
2. `board_batch.py build` writes `batch.svg` and `pending.json`. Check `pending.json`:
   - cards still "In progress" whose worker has not been merged: keep them In progress;
   - a worker that set "Review" before its branch was verified: send In progress instead;
   - `Ready: Blocked` cards whose blockers are done: set Ready.
3. Append the review-question rows and design-question rows (a small script per round that
   reads a JSON list and adds `<foreignObject data-type="table" data-miro-id=...>` blocks),
   then send everything in **one** `canvas_update_from_svg` call.
4. The update result is often larger than the tool output limit: it is saved to a file. Parse
   that JSON with Python, check `success`, `failed_items`, `skipped`, write `result_svg` to
   `<board-root>/result.svg`, then `board_batch.py commit <board-root>/result.svg`.
5. Fix the mirror for anything you patched by hand in step 2, and store new record ids (new
   review rows, design rows) from `result.svg` into `design_table.json`.
6. After a merged round, update the roadmap diagram counts (1 more call, can be in the same SVG).

## SVG rules that bit us
- Rows with `data-record-id` update existing records; rows without it create new ones.
- One `<thead>` per table per update: every row must supply every column in that header, so
  send update rows and create rows with the same column set, and send all columns of rows you
  update by hand (otherwise you blank them).
- `board_batch.py build` sends only the columns the outbox touched, so untouched descriptions
  are never wiped.
- Select cells accept only existing options; one unknown value rejects the whole update.
- Deleting (`data-deleted="true"`) is destructive. Only delete ideas the user's rules say to
  delete (processed ideas), never cards or review rows.
- Escape `<`, `>`, `&` in cell text (`html.escape`).
- Diagram inside a frame: send it inside the frame group with the frame rect.
- "Measured dimensions differ" warnings in the result are harmless for tables and kanbans.
- The MCP occasionally times out; retry once later instead of looping.
