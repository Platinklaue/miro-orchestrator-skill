# Opens an interactive Claude Code decision session for a workflow task.
#
# Each session:
#   1. gets its own git worktree on a new branch  decision/<TaskId>-<timestamp>
#      created from the latest origin/main, outside the main checkout;
#   2. runs the task's subagent (game-designer / art-director / ai-architect);
#   3. the agent commits, pushes, opens a PR and merges it into main, then writes
#      .session-done in the worktree;
#   4. this script then ends Claude, removes the worktree and closes the window.
#
# Usage: powershell -ExecutionPolicy Bypass -File Tools\Workflow\launch-task.ps1 -TaskId T15
param([Parameter(Mandatory = $true)][string]$TaskId, [switch]$DryRun)

$ErrorActionPreference = 'Stop'
$cfg = Get-Content (Join-Path $PSScriptRoot 'orchestrator.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$git = { param([string[]]$a) & git @a 2>&1 | Out-Null }   # git prints progress on stderr; never treat it as an error
$repo = (Resolve-Path (Join-Path $PSScriptRoot $cfg.repoRelative)).Path
$tasks = Get-Content (Join-Path $PSScriptRoot 'tasks.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$task = $tasks.$TaskId
if ($null -eq $task) { Write-Host "Unknown task $TaskId" -ForegroundColor Red; Start-Sleep 5; exit 1 }

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$branch = "decision/$TaskId-$stamp"
$sessionsRoot = Join-Path (Split-Path $repo -Parent) "$($cfg.projectName)_sessions"
$worktree = Join-Path $sessionsRoot "$TaskId-$stamp"
New-Item -ItemType Directory -Force $sessionsRoot | Out-Null

$host.UI.RawUI.WindowTitle = "$TaskId - $($task.title) [$($task.agent)]"
Write-Host ""
Write-Host "  $TaskId  $($task.title)" -ForegroundColor Cyan
Write-Host "  Agent: $($task.agent)   Branch: $branch" -ForegroundColor DarkGray
Write-Host "  Preparing a fresh worktree from origin/main ..." -ForegroundColor DarkGray

$ErrorActionPreference = 'Continue'
& $git @('-C', $repo, 'fetch', '--quiet', 'origin', 'main')
& $git @('-C', $repo, 'worktree', 'add', '--quiet', '-b', $branch, $worktree, 'origin/main')
if (-not (Test-Path $worktree)) { Write-Host 'Could not create the worktree.' -ForegroundColor Red; Read-Host 'Press Enter to close'; exit 1 }
& $git @('-C', $worktree, 'lfs', 'checkout')
Set-Location $worktree

$finish = @"

== Finishing protocol (do this yourself, without asking again) ==
You are working in your own git worktree on branch '$branch', created from origin/main.
When the task's questions are answered and you have written the decisions (and updated the Miro card),
and the user does not need to answer anything else:
0. Mark the board card as answered: write a JSON file into $($cfg.boardRoot)/outbox/
   named <UTC yyyyMMddTHHmmss>-decision-$TaskId.json with
   {"task": "$TaskId", "set": {"Status": "Done", "Progress": 100, "Ready": "Ready", "Description": "<100% bar> | Decided (DECISIONS $TaskId): <one line>"}}
   If building the decided feature is still to do, use instead "Status": "Todo: Claude can do", "Owner": "Claude",
   "Ready": "Ready" and a Progress of 30. The orchestrator sends it to Miro in its next batch; never leave the card on 'needs your input'.
1. git add the changed files and commit: '$($TaskId): <short summary>' plus the trailer '$($cfg.coAuthorTrailer)'.
2. git push -u origin HEAD
3. gh pr create --base main --head $branch --title '$($TaskId): <short summary>' --body '<decisions in 3-6 bullets>'
4. gh pr merge --merge --delete-branch
   If it cannot merge because main moved on, do: git fetch origin main; git rebase origin/main
   (resolve doc conflicts keeping both sides' content), git push --force-with-lease, then retry the merge.
5. Tell the user in one line what was merged (PR URL), then create the file .session-done in the worktree root
   (bash: touch .session-done). This closes the window automatically. Do not do anything after that.
If the user says they want to stop early, still commit/push/merge what was decided, then touch .session-done.
"@

$claudeExe = Join-Path $env:APPDATA 'npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe'
if (-not (Test-Path $claudeExe)) { $claudeExe = (Get-Command claude.exe -ErrorAction Stop).Source }

$allowed = @(
    'Bash(git add:*)', 'Bash(git commit:*)', 'Bash(git push:*)', 'Bash(git fetch:*)', 'Bash(git rebase:*)',
    'Bash(git status:*)', 'Bash(git diff:*)', 'Bash(git log:*)', 'Bash(gh pr create:*)', 'Bash(gh pr merge:*)',
    'Bash(gh pr view:*)', 'Bash(touch .session-done)',
    'mcp__plugin_miro_miro__canvas_read_as_svg', 'mcp__plugin_miro_miro__canvas_update_from_svg',
    'mcp__plugin_miro_miro__canvas_search'
)

function Quote([string]$s) { '"' + ($s -replace '\\(?=\\*")', '$0$0' -replace '"', '\"') + '"' }
$argList = @('--agent', $task.agent, '--allowedTools') + ($allowed | ForEach-Object { Quote $_ }) +
           @('--append-system-prompt', (Quote $finish), (Quote $task.prompt))

$marker = Join-Path $worktree '.session-done'
if ($DryRun) {
    Write-Host "DRYRUN exe: $claudeExe"; Write-Host "DRYRUN args: $($argList -join ' ')"
    New-Item -ItemType File $marker | Out-Null
} else {
$proc = Start-Process -FilePath $claudeExe -ArgumentList $argList -NoNewWindow -PassThru
while (-not $proc.HasExited) {
    if (Test-Path $marker) {
        Start-Sleep -Seconds 4          # let the agent print its last line
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        break
    }
    Start-Sleep -Milliseconds 700
}
}

# Clean up: remove the worktree when its work is merged (branch deleted on the remote) or nothing changed.
Set-Location $repo
$dirty = git -C $worktree status --porcelain 2>$null | Where-Object { $_ -notmatch '\.session-done' }
$unpushed = git -C $worktree log --oneline "origin/main..HEAD" 2>$null
$merged = (Test-Path $marker)
if ($merged -or (-not $dirty -and -not $unpushed)) {
    & $git @('-C', $repo, 'worktree', 'remove', '--force', $worktree)
    & $git @('-C', $repo, 'branch', '-D', $branch)
    & $git @('-C', $repo, 'pull', '--quiet', '--ff-only', 'origin', 'main')
    exit 0
}

Write-Host ""
Write-Host "Session ended before merging. Work is kept in $worktree (branch $branch)." -ForegroundColor Yellow
Read-Host "Press Enter to close"
