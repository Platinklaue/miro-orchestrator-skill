# Miro Orchestrator – a Claude Code skill

Run a software project from a **Miro board** with **Claude Code** as the orchestrator: Claude plans
rounds of work, runs several worker subagents in parallel (each in its own git worktree), merges and
tests their work, and keeps the board up to date - while you steer it from the board.

It grew out of a real game project (150+ cards, ~10 worker rounds a day) and is written to work for
any repository.

## What you get on the board
- **Todo and Done kanban** - every task is a card `T<number>` with a progress bar (`▰▰▰▱▱ 60%`),
  colour-coded status, milestone, owner and "Try:" steps when it is ready for you.
- **Ideas inbox** - write an idea, Claude turns it into cards.
- **Review questions** - one row per finished feature group with "How to test"; Claude can answer
  them itself from its own playtests (marked `[Claude playtest]`).
- **Design questions** - big decisions, either decided reversibly by Claude or waiting for you.
- **Dialog sessions** - cards that need your input get a *Session* link that opens a conversation
  with an agent that already knows the topic and brings options (Windows).
- **My status** - *Present* (you test and decide), *Reachable* (Claude tests, you decide),
  *AFK* (Claude tests and decides).
- **Claude Session Settings** - max parallel workers, rounds, usage pause, push/build, language...
- **How this board works** - a tutorial frame for anyone who opens the board.
- **Milestone roadmap** - green / yellow / grey with card counts.
- Words you can type any time: **AFK**, **soft sleep** (wrap up and pause), **hard sleep** (stop now),
  **wake up**.

## Requirements
- [Claude Code](https://docs.claude.com/en/docs/claude-code) with the **Miro** connector/plugin
  (the skill checks this on first use and walks you through setup if it is missing).
- A Miro account (the free plan is enough to start).
- A git repository for your project; Python 3 for the batch script; optional: `gh` (GitHub CLI) for
  dialog sessions that open pull requests, Node.js for the usage add-on.
- The dialog-session launcher scripts are PowerShell (Windows). On macOS/Linux the conversations run
  in the normal chat instead.

## Install
**With the skills CLI:**
```
npx skills add Platinklaue/miro-orchestrator-skill
```
**Or by hand:** copy the folder `skills/miro-orchestrator` to
- Windows: `C:\Users\<you>\.claude\skills\miro-orchestrator\`
- macOS/Linux: `~/.claude/skills/miro-orchestrator/`

Start a new Claude Code session in your project and say for example:
> "Set up a Miro board for this project and run it with the miro-orchestrator skill."

Claude checks the Miro connection, asks a few questions (each with a default), builds the board and
explains it.

## What's inside
| Path | Content |
|---|---|
| `SKILL.md` | Entry point: core rules, modes, where to read what |
| `references/onboarding.md` | First run: Miro check and setup, board choice, project basics, hand-over |
| `references/board-setup.md`, `visual-style.md`, `board-tutorial.md` | Board layout, colours, tutorial text |
| `references/round-loop.md`, `worker-protocol.md`, `batch-sync.md` | How rounds, workers and the batched Miro sync work |
| `references/review-cycle.md`, `modes-and-sleep.md`, `session-settings.md`, `dialog-sessions.md` | Reviews, decisions, modes, sleep, settings, dialog sessions |
| `references/usage-tracking.md` | Optional: estimate usage between `/usage` readings with ccusage |
| `scripts/board_batch.py` | Batches all board changes into one Miro update per round (Miro allows ~100 MCP calls/day) |
| `scripts/dialog/` | Local launcher for dialog sessions (Windows) |
| `scripts/usage_estimate.py` | Optional usage estimate |
| `templates/` | Worker protocol, sleep state, decisions log |

## Notes
- Workers never call Miro themselves; everything goes through one batched update per round.
- Claude never pushes untested work: worker branches are merged and the full test suite runs on the
  merged result first.
- Nothing in the skill sends data anywhere except to your own Miro board and your own git remote.

## License
MIT - see [LICENSE](LICENSE).
