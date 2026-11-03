# Dialog sessions for "Todo: needs your input" cards

Some cards need the user's taste or a real decision (art style, story, how a big feature should
work). Instead of a long chat in the main session, each such card gets its own **conversation
session**: the user clicks the card's **Session** link on the board, a terminal window opens with a
Claude Code agent that already knows the card, the context and a set of options, and talks it
through with them. When they are done, the agent writes the decisions down, turns them into todo
cards and closes itself.

## How it works (Windows; scripts in `scripts/dialog/`)
- `task-launcher.ps1` - a tiny local web server on `127.0.0.1:<launcherPort>` (default 47821).
  Opening `/task/T48` starts the session for card T48. Only ids listed in `tasks.json` are accepted;
  nothing from the request is executed. `/` lists all open sessions.
- `install-launcher.ps1` - starts the launcher now and at every login (Startup shortcut);
  `-Uninstall` removes it.
- `launch-task.ps1` - for one card: creates a fresh git worktree on `decision/<T>-<timestamp>` from
  origin/main, starts `claude --agent <agent>` with the card's prompt and a finishing protocol,
  and cleans up after the session marks itself done.
- `tasks.json` - one entry per needs-input card: `{"T48": {"title": "...", "agent": "<agent name>", "prompt": "..."}}`.
- `orchestrator.json` - project name, repo path, board folder, port, commit trailer.

## Making a card a dialog session (orchestrator or worker)
1. Write the `tasks.json` entry. The prompt must contain:
   - the card's question and the user's own words (verbatim, if it came from the ideas inbox);
   - what to read first (spec sections, decisions, related cards);
   - **3-8 concrete options** to bring to the conversation (the user asked for this: "come up with
     ideas and then ask me"), plus the open questions;
   - what to produce at the end: decisions in `Docs/DECISIONS.md` (and the spec), todo cards as
     outbox `create` files with fresh T-numbers (reserve with `mkdir <claims>/TNUM-T..`), the card
     itself set to Done.
2. Pick the agent: a project agent if one fits (e.g. game-designer, art-director), else `general-purpose`.
3. Commit `tasks.json` (`ideas: T48 ... session`).
4. Create/update the card: Status `Todo: needs your input`, Owner `You`, Session
   `http://127.0.0.1:<port>/task/T48`, Description says "Click Session to start the conversation".

## When the session finishes
The finishing protocol (in `launch-task.ps1`) makes the agent: write an outbox file setting the card
to Done (or "Todo: Claude can do" if building is still to do), commit, push, open and merge a PR
(needs `gh` and a GitHub remote; without them, it commits on its branch and the orchestrator merges
`decision/*` branches in its next round), then touch `.session-done`, which closes the window.

The orchestrator, each round: merges any `decision/*` branch that is not merged yet, syncs the new
cards from the outbox, and treats the decisions like any other recorded decision.

## Without the launcher (macOS/Linux, or the user prefers chat)
Run the same prompt as a conversation in the main session (or a subagent the user talks to via
SendMessage), and do the same finishing steps by hand.
