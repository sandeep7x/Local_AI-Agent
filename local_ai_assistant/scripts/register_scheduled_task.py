"""Register a Scheduled Task to run the reminder runner at user logon.

This script builds a schtasks command that runs the current Python
interpreter with the repository's `agents/tasks/reminder_runner.py` on
user logon. It attempts to create the task; if creation fails (usually
because elevation is required), it prints the schtasks command so you
can run it in an elevated PowerShell manually.

Usage (PowerShell):
    python scripts/register_scheduled_task.py

If you prefer to register manually, copy the printed `schtasks` command
and run it from an elevated PowerShell prompt.
"""
import os
import sys
import getpass
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable
RUNNER = REPO.joinpath('agents', 'tasks', 'reminder_runner.py')

TASK_NAME = 'LocalAI_ReminderRunner'

def build_schtasks_cmd():
    # Use ONLOGON for current user, run with limited privileges so elevation not strictly required.
    # Use /F to force overwrite if task exists.
    tr = f'"{PY}" "{RUNNER}"'
    cmd = [
        'schtasks', '/Create',
        '/SC', 'ONLOGON',
        '/RL', 'LIMITED',
        '/TN', TASK_NAME,
        '/TR', tr,
        '/F'
    ]
    return cmd

def main():
    print('Repository:', REPO)
    print('Python executable:', PY)
    print('Runner script:', RUNNER)

    cmd = build_schtasks_cmd()
    print('\nAttempting to create Scheduled Task (may require elevation)...')
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        print('Return code:', res.returncode)
        if res.returncode == 0:
            print('Scheduled Task created successfully.')
            print('Task name:', TASK_NAME)
        else:
            print('Failed to create Scheduled Task.')
            print('stdout:', res.stdout)
            print('stderr:', res.stderr)
            print('\nIf this failed due to permissions, run the following in an elevated PowerShell:')
            printable = ' '.join([f'"{c}"' if ' ' in c else c for c in cmd])
            print('\n' + printable + '\n')
    except Exception as e:
        print('Exception while creating task:', e)
        printable = ' '.join([f'"{c}"' if ' ' in c else c for c in cmd])
        print('\nRun the following in an elevated PowerShell:')
        print('\n' + printable + '\n')

if __name__ == '__main__':
    main()
