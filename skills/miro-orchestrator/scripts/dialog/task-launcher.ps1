# Local link handler for the Miro workflow board.
# Listens on http://127.0.0.1:<launcherPort from orchestrator.json> only. Opening /task/<ID> (e.g. /task/T15) starts a new
# Windows Terminal window (PowerShell tab) with the Claude Code subagent assigned to that task in tasks.json.
# Only task IDs listed in tasks.json are accepted; nothing from the request is executed.
param([int]$Port = 0)

$ErrorActionPreference = 'Stop'
$cfg = Get-Content (Join-Path $PSScriptRoot 'orchestrator.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($Port -eq 0) { $Port = [int]$cfg.launcherPort }
$tasksPath = Join-Path $PSScriptRoot 'tasks.json'
$launcher = Join-Path $PSScriptRoot 'launch-task.ps1'

function Send-Response($stream, [int]$code, [string]$status, [string]$html) {
    $body = [System.Text.Encoding]::UTF8.GetBytes($html)
    $head = "HTTP/1.1 $code $status`r`nContent-Type: text/html; charset=utf-8`r`nContent-Length: $($body.Length)`r`nCache-Control: no-store`r`nConnection: close`r`n`r`n"
    $hb = [System.Text.Encoding]::ASCII.GetBytes($head)
    $stream.Write($hb, 0, $hb.Length)
    $stream.Write($body, 0, $body.Length)
}

# Opens the decision session in a new Windows Terminal window (one tab per task).
# Falls back to a classic PowerShell console when Windows Terminal (wt.exe) is not installed.
$wt = (Get-Command wt.exe -ErrorAction SilentlyContinue).Source
function Open-TaskWindow([string]$id, $task) {
    $ps = @('powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$launcher`"", '-TaskId', $id)
    if ($wt) {
        # -w new: a separate window; --title keeps the task name on the tab; the tab closes when the session ends.
        $title = "$id - $($task.title)" -replace '[;"]', ' '
        Start-Process $wt -ArgumentList (@('-w', 'new', 'new-tab', '--title', "`"$title`"", '--suppressApplicationTitle') + $ps)
    } else {
        Start-Process $ps[0] -ArgumentList $ps[1..($ps.Count - 1)]
    }
}

function Page([string]$title, [string]$inner) {
    "<!doctype html><html><head><meta charset='utf-8'><title>$title</title><style>body{font-family:Segoe UI,sans-serif;background:#fffbed;color:#1a1a1a;padding:40px}a{color:#305bab}li{margin:6px 0}</style></head><body>$inner</body></html>"
}

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
try { $listener.Start() } catch { Write-Host "Port $Port is busy - is the launcher already running?"; exit 1 }
Write-Host "$($cfg.projectName) task launcher listening on http://127.0.0.1:$Port (Ctrl+C to stop)"

while ($true) {
    $client = $listener.AcceptTcpClient()
    try {
        $stream = $client.GetStream()
        $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::ASCII, $false, 4096, $true)
        $requestLine = $reader.ReadLine()
        if (-not $requestLine) { continue }
        $path = ($requestLine -split ' ')[1]
        $tasks = Get-Content $tasksPath -Raw -Encoding UTF8 | ConvertFrom-Json

        if ($path -match '^/task/(T\d{2,3})/?$') {
            $id = $Matches[1]
            $task = $tasks.$id
            if ($null -ne $task) {
                Open-TaskWindow $id $task
                $t = [System.Net.WebUtility]::HtmlEncode($task.title)
                Send-Response $stream 200 'OK' (Page "$id opened" "<h2>$id - $t</h2><p>A Windows Terminal window with the <b>$($task.agent)</b> agent is opening. You can close this tab.</p>")
                Write-Host "$(Get-Date -Format HH:mm:ss) opened $id ($($task.agent))"
            } else {
                Send-Response $stream 404 'Not Found' (Page 'Unknown task' "<h2>Unknown task $id</h2>")
            }
        } elseif ($path -eq '/' -or $path -eq '/tasks') {
            $items = ($tasks.PSObject.Properties | ForEach-Object {
                "<li><a href='/task/$($_.Name)'>$($_.Name) - $([System.Net.WebUtility]::HtmlEncode($_.Value.title))</a> ($($_.Value.agent))</li>" }) -join ''
            Send-Response $stream 200 'OK' (Page "$($cfg.projectName) tasks" "<h2>Tasks that need your input</h2><ul>$items</ul>")
        } else {
            Send-Response $stream 404 'Not Found' (Page 'Not found' '<h2>Not found</h2>')
        }
    } catch {
        Write-Host "Request failed: $_"
    } finally {
        $client.Close()
    }
}
