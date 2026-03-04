import os
import json
from datetime import datetime
import dateparser

REMINDERS_FILE = "reminders.json"

# Load reminders
if os.path.exists(REMINDERS_FILE):
    with open(REMINDERS_FILE, "r") as f:
        reminders = json.load(f)
else:
    reminders = []

def save_reminders():
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

def extract_reminder_details(text):
    """
    Understands natural language:
    - remind me in 10 minutes
    - remind me tomorrow at 7pm
    - remind me on 2026-02-21 at 1943
    - remind me at 6
    - remind me next Monday morning
    """

    # CLEAN TEXT
    clean = text.lower()

    # Remove common leading words
    clean = clean.replace("remind me to", "")
    clean = clean.replace("remind me", "")
    clean = clean.replace("set reminder for", "")
    clean = clean.strip()

    # Detect date and time using dateparser
    parsed_dt = dateparser.parse(clean)

    if not parsed_dt:
        return "", ""

    # Format into scheduler format
    reminder_time = parsed_dt.strftime("%Y-%m-%d %H:%M")

    # Extract text WITHOUT date/time
    # 1) Remove the date/time parts
    for part in clean.split():
        if dateparser.parse(part):
            clean = clean.replace(part, "")

    # 2) Fallback if empty
    reminder_text = clean.strip()
    if reminder_text == "":
        reminder_text = "Reminder"

    return reminder_text, reminder_time

def add_reminder(text, time_str):
    reminders.append({"text": text, "time": time_str})
    save_reminders()
    return "Reminder added successfully."

def list_reminders(check_only=False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    due = [r["text"] for r in reminders if r["time"] == now]

    if check_only:
        return due

    if reminders:
        return "\n".join([f"- {r['text']} at {r['time']}" for r in reminders])
    return "No reminders set."

def delete_reminder(text):
    global reminders
    reminders = [r for r in reminders if text.lower() not in r["text"].lower()]
    save_reminders()
    return "Reminder deleted."