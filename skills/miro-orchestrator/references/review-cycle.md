# Review cycle, self-playtests, design questions, ideas

## Review questions (cover every "Review: playtest" card)
- Before each review (and each round in AFK), make sure **every Review card is named in at
  least one review row** (`R<nn> (T<a>, T<b>) ...`). Delete questions that no longer make sense,
  add new ones, and phrase them so the user can answer in one look ("Is the Blitz yellow
  readable on parchment?"), with exact "How to test" steps and the "Current value".
- **When the user has answered** (Verdict/Rating/Your answer filled):
  1. Log every answer in `Docs/PLAYTEST.md` (date, question, verdict, answer, resulting card).
  2. Turn Tweak/Rework answers into todo cards; record taste decisions in `Docs/DECISIONS.md`.
  3. Move the covered Review cards to Done.
  4. Delete the user-answered rows (they are logged).
  5. Update the roadmap counts.
- **Self-answered rows** (AFK / Reachable): answer from your own playtest, prefix the answer
  with `[Claude playtest <date>, <build or commit>, bot <n>/<n>]`, set Keep / Tweak / Not tested
  honestly ("Not tested" + why when the bot cannot reach it; "needs your eyes" for taste).
  **Never delete a self-answered row**, even after its card is implemented - the user reviews
  them later.

## Self-playtest (Claude plays the build)
- Best: a scripted playtest bot in the project (scenarios that drive real input, take a
  screenshot per step and write a contact sheet + `summary.json`, each scenario tagged with the
  review-question ids it answers). Run it on every merged main.
- **Look at the contact sheets yourself** each round (Read the PNGs). Most real bugs were found
  this way, not by the asserts: art too busy, UI covered by fog, low-contrast characters,
  placeholder props.
- Each finding becomes either a message to the worker in that lane (if running) or a new card
  (`<stamp>-orchestrator-T<nn>-create.json`) with the screenshot path and acceptance criteria.
- If a review question cannot be answered by the bot, make a card to extend the bot
  (new scenario), so the next round can answer it.

## Design questions (big choices)
A worker or you hit a question the spec and DECISIONS.md do not answer. What happens depends on
the mode (see `modes-and-sleep.md`):
- **AFK - Claude decides:** pick the most sensible **reversible** option (config flag, data value,
  documented default), implement it, write a row `D<nn>` (Area, Context, Decision, Reversible),
  Status `Decided by Claude`. Irreversible ones (deleting content, licences, money, public
  release, renaming the product...) get `No - on hold`, the card is blocked, and they wait.
- **Reachable - the user decides:** write the row with your recommendation in *Decision*
  ("Proposal: ..."), Status `Waiting for you`, block the card (`Ready: Blocked`), and work on other
  cards. Do not implement a guess. Workers that hit one mid-task: stop that part, note it, finish
  the rest, report.
- **Present - ask directly** (AskUserQuestion), then record the answer as a row with Status
  `Answered`.
- When the user answers a row (any mode): apply it, log it in DECISIONS.md, set Status
  `Answered`, unblock the card.
- Small implementation details the spec clearly implies (names, layout, constants in line with
  existing numbers) are not "design questions" in any mode - decide and note them in the card.

## Ideas inbox
Each round (and whenever the status note says "Check the Ideas Inbox"):
1. Export rows with Status `New` as `ideas/IDEA-<id>.json` (`board_batch.py ingest` does it)
   and mark them `Read` on the board.
2. Turn each idea into 1-4 concrete todos (title, one-line description, milestone). Check SPEC,
   PLAN, DECISIONS and existing cards first; extend an existing card instead of duplicating.
3. Reserve new T-numbers atomically (`mkdir <claims-root>/TNUM-T73`, try T73, T74, ...).
4. Lane: `Todo: Claude can do` (Owner Claude) when spec/decisions/a reversible default is
   enough; `Todo: needs your input` (Owner You) for taste, money, licences, story canon.
5. Finish the idea file: `processed` (with created todos; the row is deleted from the board),
   `clarify` (question in Worker note; row set to "Needs clarification"), or `rejected` (only
   duplicates or contradictions of a recorded decision; reason in Worker note).
6. Record the direction the ideas set (vibe, style, behaviour references) in DECISIONS.md.
