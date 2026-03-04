from agents.tasks.reminder_agent import handle_set_reminder, load_reminders

cases = [
    'remind me to drink water at 15:22',
    'remind me meeting with manager on 2026-02-26 at 15:22',
    'remind me to call Raj in 1 minutes',
    'set reminder: lunch at 3pm; remind me to stand up in 1 minutes',
    'remind me tomorrow at 9am to send the report',
    'please remind me to check email after 1 minutes',
]

print('Running reminder parsing + scheduling tests...')
for c in cases:
    ok, msg = handle_set_reminder(c)
    print(c, '->', ok, msg)

print('\nCurrent reminders on disk:')
print(load_reminders())
