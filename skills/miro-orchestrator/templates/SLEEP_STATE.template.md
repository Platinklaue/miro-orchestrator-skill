# <Soft sleep | Hard sleep | Status> snapshot: <YYYY-MM-DD HH:MM> (<reason, e.g. usage window at 78%, reset 15:40; wake-up cron at 15:47>)

Round <n>. main: <commit> (<pushed | merged locally, not pushed>). Last verified: <suites and numbers>.

| Worker | Agent id | Branch | Finished (verified?) | WIP commit | Next steps |
|---|---|---|---|---|---|
| <name> | <agent id> | agent/<name> | T.. <commit> (tests ...) | <commit or none> | soft-reset the WIP; <exact steps>; outbox cards |

Pending board rows: <scratch file with review/design rows not yet sent>.
Pending docs/cleanup: <...>.
Claims kept: <T.., T..>. Slots released: <yes/no>.

On wake:
1. Read the status switch and the ideas inbox.
2. <verify / push / build steps>
3. Resume <workers> or start round <n+1> with <cards>.
