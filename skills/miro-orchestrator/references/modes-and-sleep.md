# Status switch, work modes, sleep modes, usage budget

## Reading the switch
Every round, read the single row of the "My status" table (`table_list_rows`, 1 call):
`Status` = `Present` | `Reachable - on the move` | `AFK`, plus `Note for Claude`. Treat the note
as an instruction from the user (e.g. "Check the Ideas Inbox"). The user may also just type a
mode word in chat; that overrides the board until they change the board.

## Work modes
The three modes differ in **who reviews** and **who decides**:

| | Present | Reachable - on the move | AFK |
|---|---|---|---|
| In one line | "I'm here: I test and I decide." | "I can't test, but I decide the big things." | "I'm away: you test and you decide." |
| Who playtests / answers review questions | **the user** - Claude asks the review questions and waits for answers before closing Review cards | **Claude** - self-playtest (bot + screenshots), self-answers marked `[Claude playtest]`, never deleted | **Claude** - same as Reachable |
| Design decisions (anything the spec/DECISIONS do not answer) | ask the user directly (AskUserQuestion), then record | **left to the user**: write the row in Design questions (Status `Waiting for you`), block that card (`Ready: Blocked`) and work on other cards. Claude does NOT decide them, not even reversibly. Small implementation details (names, layouts, numbers the spec implies) Claude still decides as usual. | **Claude decides**: pick the most sensible reversible option (config flag / documented default), implement it, log the row as `Decided by Claude` so the user can overrule later. Only irreversible ones (delete content, licences, money, publishing, renaming the product) go `On hold`. |
| New todos | from the user + ideas inbox | + Claude's own todos | + Claude's own todos ("Dialogue", "transitions between map and dungeon", bugs from screenshots, test-bot coverage gaps) |
| Rounds | as the settings say | continuous | continuous, until usage, settings or a sleep word stops you |
| Close unneeded apps for RAM | never | never | only if the setting allows it |
| Reporting | after each round | after each round, short; questions for the user collected in the Design questions table | after each round, short; the user reads it later |

AFK is the user's name for "keep working while I am away". Never stop to wait for a playtest or a
decision in AFK. In Reachable, never wait either - work on cards that do not depend on the open
design questions.

When the status changes:
- AFK → Reachable/Present: list the `Decided by Claude` rows since the last check so the user can
  overrule them.
- Reachable → AFK: the `Waiting for you` rows may now be decided by Claude (reversibly); say which.
- → Present: offer a playtest of everything in Review.

## AFK, soft sleep and hard sleep at a glance
These are different things: **AFK** is a *working* mode (Claude keeps going without you); **soft
sleep** and **hard sleep** are *stopping* modes (Claude pauses everything and saves where it was).

| | AFK | Soft sleep | Hard sleep |
|---|---|---|---|
| What it means | "I'm away - keep working on your own." | "Wrap up and pause." | "Stop right now." |
| Use it when | you leave for hours, overnight, a trip; you want progress when you come back | evening / usage almost used up / you want a calm stop without losing work | the PC must be free immediately (game, meeting, shutdown, something goes wrong) |
| Workers | keep running, new rounds start | each finishes its current task if that takes ≤ 10 min, otherwise saves it as a WIP commit; no new tasks | stopped at once; their work is saved as WIP commits |
| Merging / pushing | normal (after tests) | finished, verified work is merged; WIP is not | nothing is merged |
| Heavy programs (game engine, tests) | run as needed | finish, then stop | killed immediately |
| What you find afterwards | progress on the board, a short report, `[Claude playtest]` answers, `Decided by Claude` rows | `SLEEP_STATE.md` with each worker's state and next steps; the board up to date | `SLEEP_STATE.md` with each worker's WIP commit and next steps |
| How it ends | you switch "My status" (or say "Present"/"Reachable") | you say "wake up" (or Claude's own wake-up after a usage pause) | you say "wake up" |
| Typical length of the stop | - | 5-15 minutes | under a minute |

**Wake up** resumes exactly from `SLEEP_STATE.md`: each saved worker continues its task (the WIP
commit is undone into its working tree and finished), then the normal round loop goes on.

## Soft sleep ("soft sleep", or usage near the limit)
1. Tell each running worker (SendMessage): finish the current task only if it takes 10 minutes
   or less; otherwise commit the work as `WIP <task> (<worker>): soft-sleep snapshot` and stop;
   report state either way.
2. Merge workers that finished and verified; leave WIP branches unmerged.
3. Write `SLEEP_STATE.md` (template in `templates/`): per worker - agent id, branch, finished
   commits, WIP commit, exact next steps; plus what is merged/pushed, pending board rows, notes.
4. Stop. If the pause is for usage, schedule your own wake-up (below).

## Hard sleep ("hard sleep")
1. Stop all workers now (TaskStop).
2. Stop their heavy processes (game engine, test runners) and close editors the session opened.
3. Commit each worktree's uncommitted work as a separate WIP commit on its branch.
4. Release tool slots; **keep** task claims.
5. Write `SLEEP_STATE.md`. Merge nothing.
If the user asks to shut the PC down after that, only do it with their explicit permission in
that message.

## Wake up ("wake up", or your scheduled wake-up fires)
1. Read `SLEEP_STATE.md`, the status switch and the ideas inbox.
2. Resume each saved worker with SendMessage (the agent id resumes its context): "soft-reset
   your WIP commit (`git reset --soft HEAD~1`) and continue with: <next steps>".
3. Continue the round loop.

## Usage budget
- Only the user's `/usage` output shows the real numbers (5-hour window %, weekly %, reset
  times). Write them down each time the user shows them; you cannot read the meter yourself.
- Calibration from real data: 3-4 workers use roughly 10-12% of the 5-hour window per hour;
  one full round (3-4 workers, ~1 h) costs ~10-15%. Several rounds fit in one window.
- **Do not pause on a guess.** Pause only when the last real number plus your estimate is
  above ~75-80% of the 5-hour window, or the weekly limit is nearly used. (A "max 2 rounds per
  window" rule once stopped work at 38% and the user asked "Why did you stop?")
- The user may allow hitting the weekly limit early; then use every window fully.
- Pausing for usage = soft sleep + a one-shot `CronCreate` a few minutes after the window
  reset (local time; check with `date`). Cron jobs are session-only and fire only while the
  session is idle. The wake-up prompt: "WAKE UP after the usage pause. Read SLEEP_STATE.md, check
  the status switch, resume the workers ...".

## Machine resources
- Heavy tools (game engines, emulators): cap them machine-wide with slot locks
  (`mkdir <claims-root>/<tool>-slot-1|2`, released by `trap ... EXIT`). Check whether a project
  script already takes a slot itself before wrapping it (double-locking blocks both slots).
- If Claude Code stops a background command for low memory, do not restart it on your own:
  report it, let orphaned processes finish, run heavy checks one at a time, and keep rounds to
  3 workers.
