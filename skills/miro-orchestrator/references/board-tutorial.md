# "How this board works" - tutorial frame

Put this as a frame (title "How this board works") at the top-left of the board, before frame 1,
built from one title, one short intro and one sticky or text card per part (8-10 cards in a grid),
each with a small arrow or the matching colour of the part it explains. Keep the wording below
(adapt names; translate if the report language is not English). It is the user's manual.

**Intro:** "Claude runs this project from this board. You steer it with five things: ideas, your
status, review answers, design answers and the settings. Everything else Claude keeps up to date."

1. **Todo and Done (kanban).** Every piece of work is a card `T<number>`. Columns from left to
   right: *needs your input* (you decide), *Claude can do* (Claude's queue), *In progress* (a worker
   is on it; the bar ▰▰▰▱▱ shows progress), *needs input* (blocked on you), *Review: playtest*
   (finished - please try it), *Done*. Cards say what changed and how to try it ("Try:" steps).
2. **Ideas inbox.** Write any idea in a new row and leave Status on *New*. Claude reads it next
   round, turns it into cards (or a conversation card if it needs you) and removes the row.
3. **My status.** *Present*: you can playtest - Claude asks you the review questions and waits for
   your answers. *Reachable - on the move*: Claude playtests itself and keeps working, but leaves
   every design decision to you. *AFK*: Claude works fully on its own and makes the decisions
   itself (reversibly). The note field is a direct message to Claude.
4. **Todo: needs your input → Session.** Click a card's *Session* link: a window opens with an
   agent that already knows the topic and brings options. Talk it through; when you are done it
   writes the decisions down, makes the cards and closes itself.
5. **Review questions.** One row per finished feature group. *How to test* tells you what to do,
   *Current value* shows the numbers as built. Fill *Verdict* (Keep / Tweak / Rework), *Rating* and
   *Your answer*. Rows marked `[Claude playtest]` are Claude's own test notes - they stay until you
   have looked at them.
6. **Design questions.** Big choices. *Decided by Claude* rows are reversible defaults Claude
   picked (you can overrule them in *Your answer*); *On hold* rows wait for you.
7. **Claude Session Settings.** Max workers in parallel and other knobs - change a value and Claude
   follows it from the next round.
8. **Milestone roadmap.** Green done, yellow in progress, grey todo, with card counts.
9. **Vision, systems and the old ideas frames.** The project's background; they change rarely.

10. **Colours.** Green = done / ready / keep. Yellow = in progress. Orange = needs you. Red/pink =
    blocked or rework. Blue = Claude / info. Grey = not started, not tested or on hold. Each
    milestone has its own colour on the cards and the roadmap.

Footer card "Words you can type to Claude any time":
- *AFK* - "I'm away, keep working on your own" (Claude tests and decides; you find progress and a report).
- *soft sleep* - "wrap up and pause": workers finish what takes ≤ 10 minutes, the rest is saved; nothing is lost.
- *hard sleep* - "stop now": everything stops within a minute, unfinished work is saved as drafts (WIP).
- *wake up* - continue exactly where it stopped.
- *check the ideas inbox* - process new ideas now.
