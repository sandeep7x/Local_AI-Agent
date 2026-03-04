import time
from datetime import datetime
import json
import os
import time
import dateparser
from win10toast import ToastNotifier

print("🔥 RUNNING ROOT reminder_runner.py (updated)")

notifier = ToastNotifier()

# Use the project's data/reminders.json for consistency
REM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "reminders.json")


def load_reminders():
    if os.path.exists(REM_FILE):
        try:
            with open(REM_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_reminders(reminders):
    with open(REM_FILE, "w") as f:
        json.dump(reminders, f, indent=4)


def check_reminders():
    reminders = load_reminders()
    now = datetime.now()

    for r in reminders:
        if r.get("fired"):
            continue

        t = dateparser.parse(r.get("time"))
        if not t:
            continue

        diff = (now - t).total_seconds()

        # trigger only when now is at/after scheduled time and within 45s
        if diff >= 0 and diff <= 45:
            msg = r.get("text")
            print("\n🔔 Reminder Triggered:", msg, "\n", flush=True)
            # write debug log to help identify which process triggered the toast
            try:
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reminder_log.txt')
                log_path = os.path.abspath(log_path)
                with open(log_path, 'a', encoding='utf-8') as lf:
                    lf.write(f"{datetime.now().isoformat()} [root/reminder_runner] Triggered: {msg}\n")
            except Exception:
                pass
            try:
                notifier.show_toast("Reminder", msg, duration=5, threaded=False)
            except Exception:
                print(f"[Notification] Reminder: {msg}")
            r["fired"] = True
            save_reminders(reminders)


print("🔔 Root reminder background service running...")

while True:
    check_reminders()
    time.sleep(5)