from agents.knowledge.email_query_agent import search_emails_by_text
import json
res = search_emails_by_text('bharath')
print(json.dumps(res, indent=2))
