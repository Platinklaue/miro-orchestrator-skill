# Starts the task launcher now and adds it to the current user's Startup folder.
# Undo with: Tools\Workflow\install-launcher.ps1 -Uninstall
param([switch]$Uninstall)
$cfg = Get-Content (Join-Path $PSScriptRoot 'orchestrator.json') -Raw -Encoding UTF8 | ConvertFrom-Json

$shortcut = Join-Path ([Environment]::GetFolderPath('Startup')) "$($cfg.projectName) Task Launcher.lnk"
$script = Join-Path $PSScriptRoot 'task-launcher.ps1'

Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
    Where-Object { $_.CommandLine -like '*task-launcher.ps1*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

if ($Uninstall) {
    if (Test-Path $shortcut) { Remove-Item $shortcut }
    Write-Host 'Task launcher stopped and removed from Startup.'
    return
}

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($shortcut)
$lnk.TargetPath = 'powershell.exe'
$lnk.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
$lnk.WorkingDirectory = $PSScriptRoot
$lnk.Save()

Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$script`"")
Write-Host "Task launcher running on http://127.0.0.1:$($cfg.launcherPort) and added to Startup: $shortcut"
