# Board setup

How to build (or repair) a project board with the same visual aid as the Dungeon_Game board.
Before creating anything, call `canvas_get_canvas_composer_skill` once, and
`canvas_load_format_skill` for each format you create (kanban, table, diagram/flowchart, frame,
sticky). Build in as few `canvas_create_from_svg` calls as possible: one SVG can hold many items.

Ask the user only for: the board (new or existing URL), the project name, and the milestone
list if the repo has no plan yet. Everything else has a default below.

## Layout (one board, left to right, top to bottom)

```
y=-190  Title text "<Project>: Spec and Plan" + one line "Source of truth: Docs/SPEC.md and Docs/PLAN.md in the repo."

x<0     [0 How this board works] (tutorial frame, left of everything; see board-tutorial.md)

y=0     [1 Vision and Core Loop] [2 Game/Product Systems] [3 <Hard subsystem, e.g. AI>]   [Todo and Done kanban]
        frames 1800-2480 wide, 1400 high, 240 px gaps                                    x≈6400, wide (2500+)

y=1720  [4 Milestone Roadmap  (3900 wide)]  [5 Ideas from the Design Board (stickies)]

y=3500  [Gameplay review questions table] [Design questions table]  ...  [Ideas inbox table]  x≈9100
y=3900  [My status table] + three legend lines explaining Present / Reachable / AFK   [Claude Session Settings table]
```

Keep the kanban and the three tables outside frames so they can grow. Put a short instruction
text above each table (what to fill in, what Claude does with it).

Colours for every select option (lanes, milestones, owner, ready, verdicts, statuses) are in
`visual-style.md` - set them when you create each field.

## 1. Kanban "Todo and Done" (the heart of the board)
Columns (Status values, in this order):
`Todo: needs your input` · `Todo: Claude can do` · `In progress: working` · `In progress: needs input` · `Review: playtest` · `Done`

Card fields:
| Field | Type | Values / format |
|---|---|---|
| Title | text | `T<nn> <short title>` - the T-number is the key everything else uses |
| Status | select | the six columns above |
| Milestone | select | `Setup`, `M0 ...`, `M1 ...`, ..., `Design`, `M8 Polish` - the project's milestones |
| Description | text | `▰▰▰▰▱▱▱▱▱▱ 40% \| Done: ... Next: ... Try: 1) ... 2) ... [agent/<worker> <commit>]` |
| Owner | select | `Claude`, `You` |
| Ready | select | `Ready`, `Blocked` (blocked by dependencies or by an open design question) |
| Progress | number | 0-100 |
| Session | text | for "Todo: needs your input" cards: the dialog-session link `http://127.0.0.1:<port>/task/T<nn>` (see `dialog-sessions.md`); empty otherwise |

The progress bar is 10 cells of `▰` (filled) and `▱` (empty), followed by the percent. Finished
visual/feel work goes to **Review: playtest at 90%** with "Try:" or "Look at:" steps; pure
code/infra work goes to **Done at 100%**.

## 2. "Gameplay review questions" table
| Field | Type | Notes |
|---|---|---|
| Title | text | `R<nn> (T<a>, T<b>) <question>` - names every Review card it covers |
| Area | select | project areas, e.g. `Builder`, `Crawl`, `World`, `Menus and audio`, `Game loop` |
| How to test | text | exact steps |
| Current value | text | the numbers/behaviour as built, so the user can say "too slow" etc. |
| Rating | number | 1-5, filled by the user |
| Verdict | select | `Keep`, `Tweak`, `Rework`, `Not tested` |
| Your answer | text | the user's words, or `[Claude playtest <date>, <build>] ...` for self-answers |

## 3. "Design questions" table
| Field | Type | Values |
|---|---|---|
| Question | text | `D<nn> <question>` |
| Area | select | same areas as above |
| Context | text | why it came up, which card, the options |
| Decision | text | what Claude decided (or proposes) |
| Reversible | select | exactly: `Yes - config flag`, `Yes - documented default`, `No - on hold` |
| Status | select | `Waiting for you` (Reachable/Present), `Decided by Claude` (AFK, reversible), `On hold` (irreversible), `Answered` |
| Your answer | text | the user's answer; Claude processes it, records it in DECISIONS.md |

Select cells only accept existing options: sending an unknown value fails the whole update.

## 4. "Ideas inbox" table
| Field | Type | Values |
|---|---|---|
| Idea | text | the user's raw idea |
| Details | text | optional |
| Status | select | `New`, `Read`, `Needs clarification`, `Rejected` |
| Created todos | text | filled by Claude/workers |
| Worker note | text | question or reason, for clarify/rejected |

Instruction above it: "Add a row with your idea and leave Status on New. Claude turns it into
todos and removes the row."

## 5. "My status" table (the mode switch)
One row. Fields: `Who` (text, "Me"), `Status` (select: `Present`, `Reachable - on the move`,
`AFK`, with green / yellow / blue colours), `Note for Claude (optional)` (text).
Below it, three legend lines (see `modes-and-sleep.md` for the full rules):
- **Present:** I'm here - I playtest and I decide. Claude asks me the review questions and design questions and waits for my answers.
- **Reachable - on the move:** I can't playtest, but I make the design decisions. Claude playtests and answers the review questions itself; every design question goes into the Design questions table and waits for me, while Claude works on other cards.
- **AFK:** I'm away - Claude tests and decides. Claude playtests itself, answers the review questions, makes design decisions itself (reversibly, logged as "Decided by Claude"), invents new todos and keeps working.

## 4b. "Tasks for you" table + drop folder
For things only the user can provide: music, a recorded (synchronised) voice line, a specific sprite
or sound from a store, a licence answer, real-world research. One row per task, ID `U<nn>`.
| Field | Type | Values / format |
|---|---|---|
| Task | text (title) | `U<nn> <short title>` |
| Type | select | `Sound`, `Music`, `Sprite / Art`, `Voice line`, `Text / Writing`, `Licence / Research`, `Other` |
| Status | select | `Open` (orange) · `In progress` · `Delivered` (blue) · `Done` (green) · `Not needed` (grey) |
| Priority | select | `High` · `Medium` · `Low` |
| What I need | text | exactly what, mood/style, how many |
| Where it goes in the game | text | scene/system/card, so the user knows why |
| Format / specs | text | file type, length/size, naming (`U01_name.ogg`), "write the source and licence" |
| Your result | text | the user writes the file name, a link or the answer |
| Card | text | related T-number |

Instruction text above it: "Do the task, put the file into `<drop folder>` named after its ID,
write the file name, link or answer into Your result and set Status to Delivered. Claude imports it
next round and sets it to Done. Add your own rows too."
Create a local **drop folder** outside the repo (e.g. `<Project>_drop/`) with a README saying the
same. Each round read the table (filter `Status = Delivered`): import the file (right import
settings, wire it in, credits with source + licence), set the row to Done and the linked card to
Review. Add a row whenever Claude needs something only the user can make - instead of asking in chat.

## 5b. "Claude Session Settings" table
Next to "My status". Columns `Setting`, `Value`, `What it does`; rows and defaults in
`session-settings.md` (max workers at the same time, heavy tool instances, rounds, usage pause,
push/build, close apps when AFK, own todos, self-playtest, report language/detail). Above it:
"Change a value - Claude follows it from the next round."

## 5c. "How this board works" frame (tutorial)
A frame at the top-left of the board with one card per part of the board. Text in
`board-tutorial.md`. Build it during setup; update it when you add a new part.

## 6. Milestone roadmap (frame 4)
A Miro diagram from a mermaid `flowchart LR`, one node per milestone with `done / wip / todo`
classes, plus one intro line "Every milestone ends in something playable. Green is done, yellow
is in progress, grey is todo."

```
flowchart LR
  classDef done fill:#B3E65F,stroke:#6E9A24,color:#2F440B
  classDef wip fill:#FFE86D,stroke:#A28E26,color:#574900
  classDef todo fill:#E7E7E7,stroke:#9A9A9A,color:#3A3A3A
  m0["M0 Foundations<br/>12/12 done"]:::done --> m1["M1 Crawl<br/>18/20"]:::wip --> m2["M2 Builder<br/>0/9"]:::todo
```

Update node classes and `done/total` counts after every merged round. Gotcha: an update of a
diagram inside a frame must be sent inside the frame group
(`<g data-frame="..."><rect data-type="frame" .../> ...diagram... </g>`), not as a plain `<g>`.

## 7. Vision / systems frames
Frame 1: vision, design pillars, core loop (stickies + a small flowchart). Frame 2: one text card
per system with its key numbers. Frame 3: the hardest subsystem as a flowchart. Frame 5: the
user's original design-board ideas as stickies. These change rarely; do not spend Miro calls on
them during rounds.

## 8. After creating
Save every widget id and every field id (kanban, tables, design rows) into the shared board folder
(`config.json` for kanban/ideas ids, `design_table.json` for the design, review and status
tables). Field ids come from `table_list_rows` (columns) or from the create result SVG
(`data-field-id`). Then run `board_batch.py ingest` once on a full read so the mirror knows
every card.
