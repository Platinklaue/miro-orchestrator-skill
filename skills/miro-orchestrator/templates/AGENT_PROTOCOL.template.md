# Worker-agent protocol (autonomous "Todo: Claude can do" tasks)

Workers run in parallel, each in its **own git worktree**, on branch `agent/<name>`. They take
the cards the orchestrator gives them, implement and test them, commit on their own branch and
report. The orchestrator merges, verifies, pushes and updates the Miro board.

Shared folders (outside the repo):
- board: `<BOARD_ROOT>` (outbox, ideas, mirror, SLEEP_STATE.md)
- claims: `<CLAIMS_ROOT>` (task claims, tool slots)

## 1. Lanes
| Lane | Branch | Area | Owns (others only add small hooks, and say so) |
|---|---|---|---|
| <lane> | agent/<lane><n> | <milestones> | <folders> |

Shared, read-mostly: <folders>. Docs: only your own card's checkbox in PLAN.md.

## 2. Claims
`mkdir "<CLAIMS_ROOT>/T25"` before starting (the orchestrator usually does it for you). If mkdir
fails, someone has it. Never delete another worker's claim.

## 3. Doing a task
- The spec (`Docs/SPEC.md`) is the source of truth; recorded choices are in `Docs/DECISIONS.md`.
- <language, engine, style rules>.
- Never hand-edit generated files (<scenes/prefabs/assets/lockfiles>): change their generator
  and run it headless.
- Each lane has its own test assembly/folder.
- Verify before done: <unit tests>, <integration tests>, <playtest bot>, <snapshots you look at>,
  <lint/palette/format checks>.
- Commit: `T25: <what>` + `Co-Authored-By: <model> <noreply@anthropic.com>`. Never push, never merge.

## 4. Miro card updates: outbox only (never call Miro)
File `<BOARD_ROOT>/outbox/<UTC yyyyMMddTHHmmss>-<worker>-<task>-<n>.json`, one change per file:
```json
{"task": "T38", "set": {"Status": "In progress: working", "Description": "▰▰▰▰▱▱▱▱▱▱ 40% | Done: ... Next: ... [agent/<name>]", "Progress": 40}}
```
New card: `{"task": "T73", "create": {"Title": "T73 ...", "Status": "Todo: Claude can do", "Milestone": "...", "Description": "...", "Owner": "Claude", "Ready": "Ready", "Progress": 0, "Session": ""}}`

Statuses: `Todo: Claude can do`, `Todo: needs your input`, `In progress: working`,
`In progress: needs input`, `Review: playtest`, `Done`. Write at start, halfway, end. Visual or
feel work ends in **Review: playtest** (90%) with "Try:" / "Look at:" steps; other work in Done.
Design question the spec does not answer: pick a sensible reversible default, write
"Assumed: ..." in commit and card, continue.

## 5. Ideas inbox (when free)
Take `<BOARD_ROOT>/ideas/IDEA-*.json` with status `read`, claim with `mkdir <CLAIMS_ROOT>/IDEA-<id>`,
turn into 1-4 todos (reserve numbers with `mkdir <CLAIMS_ROOT>/TNUM-T73`), write `create` files,
set the file to `processed` / `clarify` / `rejected` with a note.

## 6. When to stop
After 4 finished tasks or when nothing Ready is left. Final report per task: id, commit, test
results, assumptions, things left for the user.

## 7. Worktree hygiene
- First command: `git lfs pull` (if the repo uses LFS).
- Heavy tools only inside the slot lock, one at a time:
  `C=<CLAIMS_ROOT>; S=; until { mkdir $C/<tool>-slot-1 2>/dev/null && S=1; } || { mkdir $C/<tool>-slot-2 2>/dev/null && S=2; }; do sleep 30; done; trap "rmdir $C/<tool>-slot-$S" EXIT; <command>`
  (scripts that take a slot themselves must not be wrapped).
- Scratch files only under `scratchpad/<worker>/`.
- Grep before adding a public class/module name.
- Revert re-serialisation noise in generated files you did not mean to change.
- A permission denial is reported to the orchestrator, never worked around through it.
