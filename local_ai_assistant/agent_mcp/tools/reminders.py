"""
mcp/tools/reminders.py
======================
MCP tool wrappers for the reminder subsystem.

These functions are THIN WRAPPERS around the existing
agents/tasks/reminder_agent.py functions.  No reminder logic lives here —
all business logic stays in the original agent.

Exposed MCP tools
-----------------
  reminders.set    → set a new reminder from natural language
  reminders.list   → list all pending / past reminders
  reminders.delete → delete reminders matching a keyword
"""

from __future__ import annotations

import sys
import os

# ── ensure project root is importable ──────────────────────────────────────
_MCP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # mcp/
_ROOT    = os.path.dirname(_MCP_DIR)                                       # project root
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ── import existing reminder agent (unchanged) ─────────────────────────────
from agents.tasks.reminder_agent import (
    extract_reminder_details,
    add_reminder,
    list_reminders,
    delete_reminder,
    handle_set_reminder,
)


# ══════════════════════════════════════════════════════════════════════════════
# Tool: reminders.set
# ══════════════════════════════════════════════════════════════════════════════
def reminders_set(query: str) -> dict:
    """
    Parse a natural-language reminder request and save it.

    Supports expressions such as:
      • "Remind me to call John at 15:30"
      • "Remind me to take medicine in 20 minutes"
      • "Set a reminder for tomorrow at 9 am to send the report"

    Parameters
    ----------
    query : str
        The full natural-language user utterance describing the reminder.

    Returns
    -------
    dict
        {
          "success": bool,
          "message": str,        # human-readable confirmation or error
          "reminder_text": str,  # parsed reminder text (or "" on failure)
          "reminder_time": str   # ISO-like datetime string (or "" on failure)
        }
    """
    if not query or not query.strip():
        return {
            "success": False,
            "message": "No reminder text provided.",
            "reminder_text": "",
            "reminder_time": "",
        }

    # handle_set_reminder supports multiple reminders separated by ';'
    success, msg = handle_set_reminder(query.strip())
    if success:
        # Re-parse to return structured fields for the first reminder
        text, rtime = extract_reminder_details(query.strip())
        return {
            "success": True,
            "message": msg,
            "reminder_text": text or "",
            "reminder_time": rtime or "",
        }

    # Fallback: try direct parse
    text, rtime = extract_reminder_details(query.strip())
    if rtime:
        result = add_reminder(text or "Reminder", rtime)
        return {
            "success": True,
            "message": result,
            "reminder_text": text or "Reminder",
            "reminder_time": rtime,
        }

    return {
        "success": False,
        "message": (
            "Could not parse a time from your request. "
            "Try: 'Remind me to … at HH:MM' or 'in N minutes'."
        ),
        "reminder_text": "",
        "reminder_time": "",
    }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: reminders.list
# ══════════════════════════════════════════════════════════════════════════════
def reminders_list() -> dict:
    """
    Return all reminders (pending and recently fired).

    Returns
    -------
    dict
        {
          "success": bool,
          "message": str,         # formatted text suitable for display
          "reminders": list[dict] # raw reminder objects from JSON store
        }

    Each reminder dict has the shape:
        {"text": str, "time": str, "fired": bool}
    """
    import json, os

    # Read raw data for the structured field
    _HERE = os.path.dirname(os.path.abspath(__file__))
    _PROJ = os.path.dirname(os.path.dirname(_HERE))
    rem_file = os.path.join(_PROJ, "data", "reminders.json")

    raw: list[dict] = []
    if os.path.exists(rem_file):
        try:
            with open(rem_file, "r") as f:
                raw = json.load(f)
        except Exception:
            raw = []

    formatted = list_reminders()   # delegates to agent — returns pretty string
    return {
        "success": True,
        "message": formatted,
        "reminders": raw,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: reminders.delete
# ══════════════════════════════════════════════════════════════════════════════
def reminders_delete(keyword: str) -> dict:
    """
    Delete all reminders whose text contains *keyword* (case-insensitive).

    Parameters
    ----------
    keyword : str
        A word or phrase to match against reminder text.
        Example: "call John", "medicine", "report"

    Returns
    -------
    dict
        {
          "success": bool,
          "message": str   # confirmation or error
        }
    """
    if not keyword or not keyword.strip():
        return {
            "success": False,
            "message": "Please provide a keyword to identify the reminder to delete.",
        }

    result = delete_reminder(keyword.strip())
    return {
        "success": True,
        "message": result,
    }
