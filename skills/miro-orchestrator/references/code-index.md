# Code index with SymDex (optional, recommended for big repos)

Large projects burn context when every question ("where is X defined, who calls it?") is answered by
reading whole files. SymDex builds a **local** symbol index (classes, methods, fields, call graph) so
the orchestrator and workers fetch only the lines they need. It runs on the user's machine; with
`--no-embed` nothing is sent anywhere and no API key is needed. C#, Python, TS/JS, Go, Java and more.

Use it when the repo has more than a few hundred source files, or when workers keep reading the same
big files. Skip it for small repos - grep is enough.

## Setup (ask the user first: it installs a package)
1. `pip install symdex` (user site is fine). On Windows the exe lands in
   `%APPDATA%\Python\Python3xx\Scripts\symdex.exe`, often not on PATH - note the full path.
2. Keep the index out of the repo: always pass `--state-dir <home>/.symdex`.
3. Index the source folder once (≈30 s for ~2000 files):
   `symdex --state-dir <home>/.symdex index <src-folder> --repo <project_id> --no-embed`
4. Optional skill: `npx skills add https://github.com/husnainpk/symdex --skill symdex-code-search -g -y`
   (plain instructions that tell the agent to query the index before broad reads; review it once).
5. Record the exe path, state dir and repo id in memory and in `AGENT_PROTOCOL.md` so workers use it.

## Everyday queries
| Need | Command |
|---|---|
| Where is a symbol defined | `symdex --state-dir D find <Name> --repo R` |
| Fuzzy name search | `search <part>` |
| All symbols of a file (before opening it) | `outline <path>` |
| Who calls / what it calls | `callers <Method>` / `callees <Method>` |
| Plain text across the index | `text "<words>"` |
| A token-budgeted context pack for a task | `pack "<question>"` |

Then read only the line range the result names (`Read` with offset/limit).

## Keeping it fresh
Re-index after each round's merges (`index ... --repo R --no-embed`, or `invalidate`). Workers in
worktrees query the main index for orientation; their own new code is found with grep.

## Optional: semantic search
`--embed` with a local model (`symdex[local]`, one model download) adds "search by meaning". Hosted
embedding backends send code to a provider - only with the user's explicit OK.
