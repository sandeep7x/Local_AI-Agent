Param(
    [string]$NssmPath = "C:\\nssm\\win64\\nssm.exe",
    [string]$ServiceName = "LocalAI_ReminderRunner",
    [switch]$EnableToasts = $true
)

# This script uses NSSM to register the reminder runner as a Windows service.
# Usage (run elevated PowerShell):
#   .\register_nssm_service.ps1 -NssmPath 'C:\nssm\win64\nssm.exe' -ServiceName LocalAI_ReminderRunner

if (-not (Test-Path $NssmPath)) {
    Write-Error "nssm.exe not found at $NssmPath. Download NSSM and set the path parameter."
    exit 1
}

$python = (Get-Command python).Source
$repo = Split-Path -Parent -Path $PSScriptRoot
$runner = Join-Path $repo 'agents\tasks\reminder_runner.py'

Write-Host "Using NSSM: $NssmPath"
Write-Host "Python: $python"
Write-Host "Runner: $runner"

# Install the service (nssm install <name> <path> <args>)
& $NssmPath install $ServiceName $python $runner

# Set service display name and description
& $NssmPath set $ServiceName DisplayName "Local AI - Reminder Runner"
& $NssmPath set $ServiceName Description "Runs local_ai_assistant reminder_runner.py to show desktop reminders"

# Set the working directory to the repo so relative paths resolve correctly
& $NssmPath set $ServiceName AppDirectory $repo

if ($EnableToasts) {
    Write-Host "Setting ENABLE_TOASTS=1 for service environment"
    # AppEnvironmentExtra accepts VAR=VALUE pairs; this adds the env var to the service
    & $NssmPath set $ServiceName AppEnvironmentExtra "ENABLE_TOASTS=1"
}

Write-Host "Service '$ServiceName' installed. Start it with:`n  nssm start $ServiceName`"
