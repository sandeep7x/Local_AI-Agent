NSSM Service Instructions
==========================

This project includes a PowerShell helper to register `reminder_runner.py` as
a Windows service using NSSM (Non-Sucking Service Manager).

Steps
-----

1. Download NSSM: https://nssm.cc/download
2. Extract the archive and note the path to `nssm.exe` (e.g. `C:\nssm\win64\nssm.exe`).
3. Open an elevated PowerShell (Run as Administrator).

4. Run the helper script (adjust `-NssmPath` if needed). The helper now sets
  the service working directory and, by default, configures `ENABLE_TOASTS=1`
  for the service environment so toasts are enabled when the service runs.

```powershell
Set-Location C:\Users\Sandeep\OneDrive\Desktop\local_ai_assistant\scripts
.\register_nssm_service.ps1 -NssmPath 'C:\nssm\win64\nssm.exe' -ServiceName LocalAI_ReminderRunner
```

5. Start the service:

```powershell
nssm start LocalAI_ReminderRunner
```

Notes
-----
- NSSM will run the specified Python process as a Windows service and will
  automatically restart if it crashes.
- The helper will set `ENABLE_TOASTS=1` for the service by default. If you
  need to disable it, call the helper with `-EnableToasts:$false` or update
  the NSSM service configuration manually.
- If you prefer not to use NSSM, you can create a Scheduled Task instead (see
  `scripts/register_scheduled_task.py`).
