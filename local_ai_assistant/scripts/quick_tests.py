from agents.tasks.reminder_agent import extract_reminder_details
from agents.knowledge.email_query_agent import search_emails_by_text

print('---REMINDERS---')
for t in ['remind me to drink water at 15:22', 'remind me after 10 minutes', 'remind me meeting with manager on 2026-02-26 at 15:22']:
    print(t, '->', extract_reminder_details(t))

print('\n---EMAILS---')
for k in ['abc','bharath','job','immediatly']:
    res = search_emails_by_text(k)
    print(k, '->', [m.get('id') for m in res])
