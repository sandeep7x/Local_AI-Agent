from agents.tasks.reminder_agent import extract_reminder_details, handle_set_reminder

examples = [
    "Remind me to call mom in 2 minutes",
    "Please remind me tomorrow at 5pm to submit the report",
    "remind me at 16:25 to go to temple",
    "set a reminder for next monday at 9am to attend meeting",
    "in 10 seconds remind me to check oven",
    "after 30 seconds call home",
    "remind me to drink water every day at 15:00",  # repeating not supported, but parse time
    "remind me to pay rent on 2026-04-01",
    "remind me in 1 hour to stretch",
    "please set a reminder: take meds at 21:30"
]

for ex in examples:
    msg, t = extract_reminder_details(ex)
    print(f"Input: {ex}")
    print(f"Parsed message: {msg!r}, time: {t}")
    print()

print('Testing handle_set_reminder (scheduling):')
ok, resp = handle_set_reminder('remind me in 1 minute to test quick reminder')
print('handle_set_reminder:', ok, resp)
