# Claude Session Settings (a table on the board)

A small table next to "My status" where the user turns the knobs of the loop. Claude reads it
together with "My status" at the start of every round (same `table_list_rows` call budget: 1 call)
and follows it. Changing a value never needs a chat message.

## Table "Claude Session Settings"
Columns: `Setting` (text), `Value` (select or number), `What it does` (text). One row per setting.
Select options are listed per row below; create the column as **text** if Miro cannot hold
different options per row, and validate the value yourself (fall back to the default and say so).

| Setting | Values (default **bold**) | What Claude does |
|---|---|---|
| Max workers at the same time | 1, 2, **3**, 4, 5, 6 | Never runs more parallel worker subagents than this. With heavy tools (game engines) and 16 GB RAM, 2-3 is the safe range. |
| Max heavy tool instances | 1, **2**, 3 | Size of the slot lock (e.g. Unity/emulator instances machine-wide). |
| Rounds | **Continuous**, One round then wait, Paused | Continuous: next round starts after the last one is shipped. One round: stop after shipping and wait for "go". Paused: like soft sleep. |
| Usage pause at | 70%, **80%**, 90% | Soft-sleep when the last real /usage number plus the estimate reaches this share of the 5-hour window; wake after the reset. |
| Weekly limit | **Use it fully**, Spread over the week | Spread: aim for ~1/7 of the weekly limit per day. |
| Push to main | **After all tests pass**, Never (I merge myself) | Never: keep merged work on a local branch `staging` and report. |
| Build after each round | **Yes**, No | Build the deliverable (exe, app) after a verified merge. |
| Close unneeded apps when AFK | Yes, **No** | Only while status is AFK: close RAM-heavy apps the work does not need (never VPN/remote access tools); list them in the report. |
| Own todos when the board runs dry | **Yes**, No | Invent cards from playtest findings, test gaps and polish. |
| Self-playtest | **Bot + screenshots**, Tests only | Whether Claude looks at screenshots/contact sheets each round. |
| Usage tracking | **Off**, ccusage | ccusage: estimate the window % between the user's /usage readings (`usage-tracking.md`). |
| Report language | **Same as the user**, English, German, ... | Language of chat reports and card texts. |
| Report detail | Short, **Normal**, Detailed | Length of the round report. |

Add project-specific rows when useful (e.g. "Target platform build", "Art pass allowed").

## Reading it
- Read it each round right after "My status". Cache the values in `<board-root>/settings.json`
  with a timestamp; use the cache if a Miro call fails.
- If a value changed since the last round, say so in one line ("Max workers is now 2 - I'll
  run 2 workers.").
- A value in chat ("only 2 workers please") wins until the user changes the table; offer to
  update the table for them.
