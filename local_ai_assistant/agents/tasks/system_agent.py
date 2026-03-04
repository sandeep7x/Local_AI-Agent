# system_agent.py

import os
import subprocess
import platform

def open_application(app_name):
    """
    Opens applications based on OS.
    Supports: Windows (your system)
    """

    app_name = app_name.lower()
    system = platform.system()

    if system == "Windows":
        return open_app_windows(app_name)

    return "Unsupported operating system."


def open_app_windows(app_name):
    """
    Add more commands here as needed.
    """

    apps = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "notepad": "notepad",
        "calculator": "calc",
        "vs code": r"C:\Users\Sandeep\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "explorer": "explorer",
    }

    for key in apps:
        if key in app_name:
            try:
                subprocess.Popen(apps[key])
                return f"Opening {key}..."
            except Exception as e:
                return f"Failed to open {key}: {str(e)}"

    return "I don't recognize that application. Please add it to system_agent.py"