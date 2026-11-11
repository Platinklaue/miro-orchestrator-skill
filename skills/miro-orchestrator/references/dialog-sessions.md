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

## Session builder (how the orchestrator writes a session)
Every needs-input card gets a `tasks.json` entry built from this template:
```json
"T173": { "title": "Slaves: prisoners as workers, quarters, slave trade", "agent": "game-designer", "prompt": "..." }
```
The prompt (the agent has no other context) has these parts, in this order:
1. **Role and goal:** "You are the <area> designer for <project>. Talk this card through with the user and settle it."
2. **The user's words:** the idea row / review answer verbatim, with its date.
3. **What exists:** 3-6 bullets of what the project already does here (checked in the code - grep or the
   code index, `code-index.md` - not from memory), plus the files/doc sections/DECISIONS entries to read first.
4. **Options:** 3-8 concrete, different options, one line each with the trade-off; mark the one you would
   pick and why; include "keep as is" when it is real.
5. **Open questions:** the 2-5 decisions the user must make, in the order to ask them.
6. **Tone and pace:** one question at a time, the user's language, numbered options, accept "you decide".
7. **Finish:** decisions into `Docs/DECISIONS.md` (`## T<nn> ...`, date, "Decided by the user") and the spec;
   build cards as outbox `create` files with reserved numbers; this card Done; the finishing protocol below.
Then commit `tasks.json`, set the card `Todo: needs your input`, Owner `You`, Session = the link,
Description "Click Session to talk it through: <one-line topic>".

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

## Opening sessions from a laptop or phone (Remote Control)
The launcher link (`http://127.0.0.1:<port>/...`) only works on the machine that runs the project. Claude
Code's **Remote Control** makes a session that runs on that machine visible in **claude.ai/code** and the
**Claude app** (same claude.ai account; Pro/Max/Team/Enterprise). The session, files, tools and the
project's editor stay on the desktop, which must stay on. Docs: https://code.claude.com/docs/en/remote-control.md
Cloud sessions (`claude --cloud`) are not used here: they have no local engine/editor and no local MCP.

**One-time setup on the desktop (interactive, the user does it):** in the repo folder run
`claude remote-control` once and answer the "Enable Remote Control?" and workspace-trust prompts
(scripted starts fail with "Workspace not trusted" until then).

**A. Sessions started on the desktop show up remotely.** `launch-task.ps1` adds
`--remote-control "<T-id> <title>"` (turn off with `-NoRemote`). Start the session from the board on the
desktop (or let the orchestrator start it), then on the laptop open claude.ai/code or the app → the
session with that name (computer icon, green dot) → talk. The terminal also prints a URL / QR code.

**B. Start a session from the laptop.** Keep a Remote Control server running on the desktop:
`claude remote-control --name "<Project> dialogs" --spawn worktree` (in the repo folder; a startup
shortcut can run it at login). On the laptop: claude.ai/code → that server → new session → type
`/task T<nn>`. The project command `.claude/commands/task.md` loads the card's `tasks.json` entry, takes
on its agent, branches `decision/T<nn>-<stamp>` and follows the same finishing protocol (without
`.session-done`). The Miro card's Session link stays the desktop link; its Description says
"From another device: claude.ai/code → <Project> dialogs → /task T<nn>".

Not documented / to verify on first use: whether `--agent` + a starting prompt combine with
`--remote-control` (if not, use route B), and getting the session URL programmatically (not available;
find the session by name).
