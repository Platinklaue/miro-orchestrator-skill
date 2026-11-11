---
description: Start a "needs your input" dialog session for a board card, e.g. /task T48 (works from the laptop via Remote Control)
argument-hint: T<nn>
---

Start the dialog session for board card **$ARGUMENTS**.

1. Read `Tools/Workflow/tasks.json` and take the entry `$ARGUMENTS` (title, agent, prompt). If there is no such entry,
   list the open entries (id + title) and stop.
2. Read `.claude/agents/<agent>.md` and act as that agent for the rest of this session.
3. Work on a fresh branch: `git fetch origin main` and `git switch -c decision/$ARGUMENTS-<yyyyMMdd-HHmmss> origin/main`
   (if this session was spawned in its own worktree, branch there; never work on main directly).
4. Follow the entry's prompt: talk it through with the user, one question at a time, options as a numbered list.
5. Finish exactly like a launcher session (see the finishing protocol in `Tools/Workflow/launch-task.ps1`):
   outbox file setting the card Done (or "Todo: Claude can do" if building is still to do), commit
   `$ARGUMENTS: <summary>` with the co-author trailer, push, `gh pr create` + `gh pr merge --merge --delete-branch`
   (rebase on origin/main if needed). Skip the `.session-done` step; tell the user in one line what was merged.
