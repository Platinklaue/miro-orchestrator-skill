# Visual style: colours and colour-coded cards

The board should be pleasant to look at and readable at a glance: every select value has its own
colour, colours mean the same thing everywhere, and there are few strong colours. Set the colours
when creating the kanban and tables (select options carry a colour: `data-options="Value:#hex, ..."`
on the `<th data-type="select">`), and keep them when adding options later.

## Rules
- **Colour = meaning, used consistently.** Green = done / ready / keep. Yellow/amber = in progress /
  waiting. Orange = needs the user. Red/pink = blocked / problem / rework. Blue = Claude / info.
  Grey = not started / not tested / on hold.
- **Pastel backgrounds, dark text.** Miro draws select values as chips; pastel chips with dark text
  read best. Use at most one saturated colour per field (e.g. the "Done" green). Never a dark chip
  with dark text.
- **One colour per milestone**, from a soft rainbow, in roadmap order, so the cards of one milestone
  are recognisable in every column. The roadmap nodes use the same hues.
- **Progress** is a number field shown as percent, plus the 10-cell bar `▰▰▰▰▱▱▱▱▱▱ 40%` at the start
  of the description, so progress is visible on the card face.
- Frames: white or very light backgrounds; stickies in the frame's theme colour; one accent colour
  per frame title line at most.

## Kanban fields (as in the reference project, with the recommended fixes)
| Field | Option → colour | Notes |
|---|---|---|
| **Status** (the lanes) | `Todo: needs your input` #ffbd83 (orange) · `Todo: Claude can do` #f8d3af (light peach) · `In progress: working` #fff6b6 (yellow) · `In progress: needs input` #ffc6c6 (pink) · `Review: playtest` #c6dcff (light blue) · `Done` #adf0c7 (light green) | The reference board had `In progress: working` as dark brown #9b4a08 and `Done` as strong green #2dc75c; prefer the pastel versions for readable chips. |
| **Milestone** | `Setup` #e7e7e7 · `Design` #dedaff · `M0` #c6dcff · `M1` #adf0c7 · `M2` #fff6b6 · `M3` #ffc6c6 · `M4` #c4f0f0 · `M5` #f8d3af · `M6` #dedaff · `M7` #ffbd83 · `M8` #d5f692 · `M9` #f5d0fe | One hue per milestone (the reference board used one blue for all - avoid). Add more hues in the same soft range. |
| **Owner** | `Claude` #c6dcff (blue) · `You` #ffbd83 (orange) · `Claude and you` #dedaff (lavender) | Orange = the user is needed, everywhere on the board. |
| **Ready** | `Ready` #adf0c7 (green) · `Blocked` #ffc6c6 (pink/red) | The reference board had two similar yellows; make them clearly different. |
| **Progress** | number, 0 decimals, shown as percent | |
| **Session** | link | dialog-session URL for needs-your-input cards. |

## Tables
| Table | Field → colours |
|---|---|
| Review questions | **Verdict:** `Keep` #adf0c7 · `Tweak` #fff6b6 · `Rework` #ffc6c6 · `Not tested` #e7e7e7. **Area:** one pastel per area, e.g. `Builder` #c6dcff · `Crawl` #ffc6c6 · `World` #adf0c7 · `Menus and audio` #dedaff · `Game loop` #fff6b6. |
| Design questions | **Status:** `Waiting for you` #ffbd83 · `Decided by Claude` #c6dcff · `On hold` #e7e7e7 · `Answered` #adf0c7. **Reversible:** `Yes - config flag` #adf0c7 · `Yes - documented default` #d5f692 · `No - on hold` #ffc6c6. **Area:** same colours as in the review table. |
| Ideas inbox | **Status:** `New` #fff6b6 · `Read` #c6dcff · `Needs clarification` #f8d3af · `Rejected` #e7e7e7. |
| My status | `Present` #adf0c7 (green) · `Reachable - on the move` #fff6b6 (yellow) · `AFK` #c6dcff (blue). |
| Claude Session Settings | Values neutral (#e7e7e7) except on/off style values: `Yes`/`Continuous` #adf0c7, `No`/`Paused` #ffc6c6. |

## Roadmap diagram
`classDef done fill:#B3E65F,stroke:#6E9A24,color:#2F440B` · `classDef wip fill:#FFE86D,stroke:#A28E26,color:#574900` ·
`classDef todo fill:#E7E7E7,stroke:#9A9A9A,color:#3A3A3A`. Optionally tint each node's stroke with its
milestone colour.

## Legends
Every table gets a one-line legend above it naming the colours that matter ("green = keep, yellow =
tweak, red = rework"). The tutorial frame (`board-tutorial.md`) repeats the colour meanings once.
