from agents.tasks.email_agent import EmailAgent

agent = EmailAgent()

emails = agent.fetch_unread_emails()
print("Fetched emails:", emails)

agent.save_emails_to_cache(emails)
print("Emails saved to cache.")