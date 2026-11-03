# One round, start to finish

## 0. Before the round
- Read `SLEEP_STATE.md` if it exists, the "My status" row, and the ideas inbox (1-2 Miro calls).
- Process new ideas (see `review-cycle.md`), process answered review and design questions.
- Check usage against the last real `/usage` numbers (see `modes-and-sleep.md`).

## 1. Plan
- Pick 3-6 cards that do not touch the same files. Group by **lane** (e.g. crawl, builder, sim,
  ui, art, qa). Give each worker 1-4 cards, in order, with the card text and the doc sections to
  read. Name workers `<lane><n>` (art5, ui6, map8); branch `agent/<name>`.
- With heavy tools (game engine, emulators) on one PC: max 3 workers when memory is tight.
- Claim every card first: `mkdir <claims-root>/T<nn>` (orchestrator claims for the worker).
- Add your own todos when the board runs dry: bugs from your playtest, coverage gaps in the
  test bot, polish the user mentioned, follow-ups workers reported. Write them as `create` files.

## 2. Launch
`Agent` tool, `isolation: "worktree"`, `run_in_background: true`, all workers in one message.
Each prompt states: who they are, branch, base commit, "the user is AFK, do not ask, decide
reversibly and note assumptions", "read and follow AGENT_PROTOCOL.md (esp. worktree hygiene)",
the cards with full context, acceptance criteria (tests, bot, snapshots, palette checks...),
"one commit per card, outbox JSON per card, final report: commits, test table, snapshot paths,
assumptions, things left for the user". Tell them which other workers run and which files to
avoid.

## 3. While they work
- Do not poll. React to their reports; answer their messages with `SendMessage`.
- Forward findings from your own playtest to the worker whose lane it is.
- Prepare the Miro rows for the round (review questions, design rows) in a scratch script.

## 4. Merge (one worker at a time, as each reports)
- `git merge --no-ff agent/<name> -m "Merge agent/<name>: T.. ..."`.
- Typical conflicts and fixes: shared JSON lists (union by key, never pick one side), docs with
  two appended sections (keep both), two classes with the same name (alias or rename).
- Remove the worktree and branch once merged (`git worktree remove`; on Windows long paths use
  `Remove-Item -LiteralPath "\\?\C:\...\agent-xxx" -Recurse -Force`, then `git worktree prune`;
  a folder locked by a still-exiting process: retry later). Release the claims.

## 5. Verify the merged tree (before any push)
- Full suites + the playtest bot on main, one heavy instance at a time. If a scene/asset
  generator exists, regenerate and revert pure re-serialisation noise; keep real changes.
- A failure that passes when rerun alone is a timing flake: make the test robust, do not
  just rerun. A failure that repeats in a fresh start is a real bug: file a card.
- A worker's green run counts for main only if `git diff HEAD agent/<name>` is empty after the merge.

## 6. Ship
- Commit fixes (with the project's co-author trailer), `git push`, build the deliverable.
- One batched Miro update (see `batch-sync.md`): cards, review rows, design rows, roadmap.
- Update `SLEEP_STATE.md` (the round snapshot) and report to the user in a few lines:
  what merged, test numbers, what is on the board for them, what runs next.
- Then start the next round right away if the mode and the usage allow it.
