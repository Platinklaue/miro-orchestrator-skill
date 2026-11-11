# Worker protocol

Each project gets its own `Tools/Workflow/AGENT_PROTOCOL.md`, made from
`templates/AGENT_PROTOCOL.template.md`. Workers read it first; the orchestrator's launch prompt
only adds the cards and acceptance criteria. Keep the protocol short and update it when a
round teaches you something (add a numbered "hygiene" rule, never a long story).

## What the protocol must define
1. **Lanes:** a table of worker kinds (e.g. crawl, builder, sim, ui, art, qa, infra), their
   branch prefix and the folders each one owns. Other lanes only make small, additive hooks
   there and say so in their report.
2. **Claims:** atomic `mkdir <claims-root>/T<nn>`; never delete another's claim.
3. **Doing a task:** spec is the source of truth; code style; never hand-edit generated files
   (scenes/prefabs/assets) - write a generator and run it headless; tests per lane in their own
   test assembly; one heavy process per worktree.
4. **Verify before done:** the suites and checks the project has (unit, integration, playtest
   bot, visual snapshots that the worker looks at, lint/palette checks).
5. **Commit:** `T<nn>: <what>` + the co-author trailer; never push, never merge.
6. **Board updates:** only outbox JSON (format in `batch-sync.md`); start / halfway / end.
   Visual or feel work ends in `Review: playtest` (90%) with "Try:"/"Look at:" steps.
7. **Design questions:** pick a sensible reversible default, note "Assumed: ..." in the commit
   and the card, continue. "In progress: needs input" only if truly blocked.
8. **Ideas inbox duty** when free (see `review-cycle.md`).
9. **Stop rule:** after 4 finished tasks or when nothing Ready is left; final report lists per
   task: id, commit, test results, assumptions, things left for the user.
10. **Worktree hygiene** (learned the hard way):
    - first command in a new worktree: `git lfs pull` (fresh worktrees hold LFS pointers);
    - every heavy command inside the slot lock; one at a time; no long background chains;
    - shared scratchpad: own sub-folder `scratchpad/<worker>/` only;
    - grep before adding a public class name (two lanes adding the same class broke a merge);
    - if the project has a code index (`code-index.md`), query it before opening big files;
    - revert pure re-serialisation noise from generated files you did not mean to change;
    - if an action is denied by the permission system, report it - do not ask the orchestrator
      to do it for you.

## Launch prompt skeleton
```
You are worker **<name>** on <project>, working autonomously in your own git worktree on branch
agent/<name> (`git checkout -b agent/<name>` if needed; start from main <commit>). The user is
AFK; do not ask questions - decide reversibly and note assumptions.
First read and follow Tools/Workflow/AGENT_PROTOCOL.md (esp. worktree hygiene). Read <docs/sections>.
Your cards (claimed for you), in order:
1. **T<nn> <title>** - <full card text, context, screenshots, what "good" looks like>
2. ...
Other workers in parallel: <name> (<area>) - stay out of those files.
Acceptance: <tests>, <bot n/n>, <snapshots>, <checks>. One commit per card; outbox JSON per card.
Final report: commits, test table, snapshot paths, assumptions, things left for the user.
```
