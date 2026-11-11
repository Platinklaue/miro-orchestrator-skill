# Building cards: todo, in progress, review, done

How a card is born, how it moves, and how finished cards are folded so the kanban stays short.
Field definitions are in `board-setup.md` §1; the outbox format in `batch-sync.md`.

## 1. Card anatomy
| Field | How to fill it |
|---|---|
| Title | `T<nn> <short title in plain words>` (≤ 70 chars). Reserve the number first: `mkdir <claims>/TNUM-T<nn>` (atomic; take the next free one). Never reuse a number. |
| Status | one of the six kanban columns (exact spelling, see `board-setup.md`). |
| Milestone | an existing option only (an unknown value fails the whole update). Map new areas to the nearest milestone. |
| Description | `<bar> <pct>% \| <text>`; the bar is 10 cells `▰`/`▱`. Text rules below. |
| Owner | `Claude` for build cards, `You` for cards waiting on the user (needs input, review summaries). |
| Ready | `Ready`, or `Blocked` when it depends on another card / a parked idea / a design answer. |
| Progress | the same number as the bar (0-100). |
| Session | only on `Todo: needs your input` cards: the dialog-session link (`dialog-sessions.md`). |

**Description text rules** (the user reads these, often on a phone):
- Plain short English, no code words unless needed; say *what the player/user sees*.
- Todo cards: where it came from ("From your idea '...'", "Found by <worker> in T<nn>",
  "From the visual review V26"), what to build, acceptance hints, related cards.
- Review cards: what changed, then `Try:` with a debug save / keys / clicks, then
  `Decided by Claude, reversible:` with the defaults chosen, then the verification line
  (`Verified on main <hash>: <suite counts>`), then `[agent/<worker> <commit>]`.
- Done cards: one line of what is now true + where the details are.

## 2. Where cards come from
| Source | Who writes it | How |
|---|---|---|
| Ideas inbox row | orchestrator | split into build cards (`Todo: Claude can do`) and taste/decision cards (`Todo: needs your input` + session). Fill the row's *Created todos* and *Worker note*, set it to `Read`. |
| Old idea lists, specs, reviews | orchestrator | check what already exists in the code first (grep / the code index); only the gaps become cards. |
| A worker finds a bug outside its cards | worker | outbox `create` file with a reserved number; never fixes it silently. |
| Follow-ups after a merge | orchestrator | small cards for what the worker left open ("Left open" in its report). |
| Recurring work (audits) | orchestrator | one card that stays, its description updated each time. |

## 3. Lifecycle
```
Todo: needs your input --(session done)--> Todo: Claude can do --(claimed)--> In progress: working
   --(merged + verified)--> Review: playtest 90%   (visual / feel / gameplay)
                         --> Done 100%             (pure code, refactor, infra, docs)
Review: playtest --(user verdict Keep / Claude self-playtest in AFK)--> folded into a Review summary, later Done
```
- Start of a round: the orchestrator sets the claimed cards to `In progress: working` (in the round's
  board call), workers add their own start/halfway/end outbox files.
- A worker whose card is unfinished at a stop (sleep, usage) commits `WIP T<nn>: ...` and the card
  stays `In progress` with the remaining steps in its description.
- Never move a card to Review/Done before the **merged tree** is verified (tests + bot).

## 4. Folding: keep the kanban short (every round)
Finished cards do not stay as single cards. Per area there is **one summary card**:
- `Review summary: <Area> (<n> cards)` - Status `Review: playtest`, Owner `You`, 90 %. Description:
  `Summary of <n> cards waiting for your playtest. How to test: review table row '<Area>'. Full card
  texts: Docs/REVIEW_CARDS_ARCHIVE.md. Cards: T.. <title>; T.. <title (try: ...)>; ... Blocked earlier: T..`.
- `Done summary: <Milestone> (<n> tasks)` - Status `Done`, 100 %, lists the finished titles,
  full texts in `Docs/DONE_ARCHIVE.md`.

Fold step (one script per round, e.g. `scratchpad/rNN_fold.py`):
1. Collect the latest outbox `set` per card (the newest file wins; a fix worker's text is appended,
   not replacing the feature text).
2. Start from the summaries as last posted (keep the previous round's fold SVG; read the board only
   if you lost it). Never rebuild a summary from memory.
3. For each finished card: append `T<nn> <title> (try: ...)` before `Blocked earlier:`, bump `(<n> cards)`
   and `Summary of <n> cards`, append the full card text + the verification line to the archive file,
   and mark the single card `data-deleted="true"` (deletion of folded cards is part of the normal loop).
4. Send: one call for new/changed cards (creates have no record id), one for the summaries + deletions.
   Same widget in one SVG twice is not allowed - split calls when the headers differ.
5. Update the local mirror (drop deleted record ids, add the ids the result returned), archive the
   outbox to `archive/outbox_rNN/`, release the claims.

Board-table cleanup (same round): ideas the user marked `Read - noted` → archive to
`Docs/BOARD_ARCHIVE.md` and delete; design questions `Confirmed by you` / `Changed by you` (acted on)
→ archive and delete. `Decided by Claude` / `On hold` rows stay until the user looks.

## 5. Pitfalls seen in practice
- A worker's "done" outbox text can describe only its last fix; append, don't replace.
- Select cells accept existing options only; check the milestone list before creating.
- Writing a field you didn't mean to (e.g. sending Description with an empty value) wipes it: send
  only the columns you have real values for (separate SVG/call per header set).
- Keep the previous round's posted summary text on disk; it is the base for the next fold.
