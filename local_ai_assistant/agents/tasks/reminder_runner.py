import time
from datetime import datetime
import json
import os
import dateparser
from win10toast import ToastNotifier

print("🔥 RUNNING LATEST reminder_runner.py")

notifier = ToastNotifier()

# ---------------------
# FILE PATH
# ---------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
REM_FILE = os.path.join(PROJECT_ROOT, "data", "reminders.json")

print("Reminder file path:", REM_FILE)


# ---------------------
# LOAD / SAVE
# ---------------------
def load_reminders():
    if os.path.exists(REM_FILE):
        try:
            with open(REM_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []


def save_reminders(rem_list):
    with open(REM_FILE, "w") as f:
        json.dump(rem_list, f, indent=4)


# ---------------------
# CHECK REMINDERS
# ---------------------
def check_reminders():
    reminders = load_reminders()
    now = datetime.now()

    for r in reminders:
        if r.get("fired"):
            continue

        t = dateparser.parse(r["time"])
        if not t:
            continue

        # Compute difference (seconds) where positive means now is after scheduled time
        diff = (now - t).total_seconds()

        # trigger if now is at or after scheduled time and within a 45-second window
        if diff >= 0 and diff <= 45:
            msg = r["text"]

            print("\n🔔 Reminder Triggered:", msg, "\n", flush=True)

            # write debug log to help identify which process triggered the toast
            try:
                log_path = os.path.join(PROJECT_ROOT, 'reminder_log.txt')
                with open(log_path, 'a', encoding='utf-8') as lf:
                    lf.write(f"{datetime.now().isoformat()} [agents/tasks/reminder_runner] Triggered: {msg}\n")
            except Exception:
                pass

            # use non-threaded to avoid pywin32 callback issues
            try:
                notifier.show_toast("Reminder", msg, duration=5, threaded=False)
            except Exception:
                # fallback to console if toast fails
                print(f"[Notification] Reminder: {msg}")

            r["fired"] = True
            save_reminders(reminders)


print("🔔 Reminder background service running...")

while True:
    check_reminders()
    time.sleep(5)
