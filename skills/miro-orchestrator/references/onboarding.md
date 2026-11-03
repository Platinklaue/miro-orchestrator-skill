# First run: check Miro, set everything up, explain the board

Run this the first time the skill is used in a project (no `<board-root>/config.json` yet), or
whenever a Miro call fails with an auth/connection error. Be friendly and short: the user may have
never used Miro or Claude Code plugins. One step at a time; confirm each step worked before the
next. Never ask for passwords or tokens in chat.

## Step 1 - Is Miro connected?
1. Look for Miro tools (`ToolSearch` query `miro`). If tools like `mcp__plugin_miro_miro__user_who_am_i`
   exist, call it.
   - It returns a user and team: Miro works. Say "You're connected to Miro as <name> (team <team>)."
     and go to Step 2.
   - It errors with auth / not connected: go to 1b.
2. No Miro tools at all, or 1b (not signed in): walk the user through setup.
   - **No Miro account yet:** "Create a free account at https://miro.com/signup (Google/Microsoft
     sign-in works). The free plan is enough to start; it limits the number of editable boards, so
     we use one board for the whole project." Wait until they say done.
   - **Connect Claude Code to Miro:** the Miro plugin / MCP server must be installed and signed in.
     Tell them to run `/plugin` in Claude Code, find **Miro** in the marketplace and install it (or,
     if their setup uses MCP servers directly, add Miro's MCP server as described in Miro's docs:
     https://developers.miro.com - search "MCP"). Then restart Claude Code if asked, and complete the
     browser sign-in that opens. Do not guess commands you have not verified; if something differs
     on their machine, ask them what they see.
   - Check again with `user_who_am_i`. Loop until it works or the user wants to stop.
3. Miro limits: about **100 MCP calls per day**. Tell the user once: "Claude batches all board updates
   (2-4 calls per round), so this is plenty."

## Step 2 - Which board?
Ask (AskUserQuestion): "Create a new board for this project (recommended) / Use an existing board
(paste the link)". For a new board use `board_create` with the project name. Save the board URL.

## Step 3 - Project basics (ask only what you can't find)
Read the repo first (README, docs, plan, git remote). Then ask in ONE question set, with defaults:
- Project name (default: repo folder name).
- Milestones (default: read from the plan, else propose 5-8 and let them edit).
- Areas for review questions (default: derived from the milestones).
- Max workers in parallel (default 3; see `session-settings.md`).
- Language for board texts and reports (default: the language the user writes in).

## Step 4 - Build the board
Follow `board-setup.md`: frames, kanban, the tables, **Claude Session Settings**, **How this board
works** tutorial frame, roadmap. Fill the kanban from the project's plan (one card per todo).

## Step 5 - Local plumbing (one-time, on the user's PC)
- Board folder `<board-root>` + claims folder, `config.json`, `design_table.json` (ids), first
  `board_batch.py ingest`.
- Copy `scripts/board_batch.py` to the project's `Tools/Workflow/`.
- Write the project's `AGENT_PROTOCOL.md` from the template.
- Dialog sessions for "Todo: needs your input" cards: copy `scripts/dialog/*` to `Tools/Workflow/`,
  create `orchestrator.json` from the example, start the launcher (`install-launcher.ps1`, Windows;
  on macOS/Linux tell the user it is Windows-only for now and offer to run sessions from chat
  instead). See `dialog-sessions.md`.
- `Docs/DECISIONS.md` from the template.

## Step 6 - Explain and hand over
Give the user a 6-line tour (point at the tutorial frame on the board):
1. Drop ideas into **Ideas inbox** - Claude turns them into cards.
2. Set **My status** (Present / Reachable / AFK) - Claude adapts how it works.
3. Cards you must decide sit in **Todo: needs your input** - click its Session link to talk it through.
4. Finished features land in **Review: playtest** - answer the matching row in **Review questions**.
5. Big choices Claude made or needs are in **Design questions**.
6. **Claude Session Settings** - max workers and other knobs.
Then ask: "Shall I start the first round?"
