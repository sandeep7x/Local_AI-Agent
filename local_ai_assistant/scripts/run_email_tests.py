import sys
from pathlib import Path

# Ensure project root is on sys.path so local imports work when running scripts
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.knowledge.email_query_agent import search_emails_by_text, load_all_emails
from agents.knowledge.email_summarizer_agent import handle_email_summary

queries = [
    # short/direct
    'abc',
    'Bharath',
    'job',
    'susmitha',
    'meeting',
    # natural language variants
    'show me emails from Bharath',
    'emails about job confirmation',
    'any urgent messages',
    'summarize emails regarding meeting',
    'from susmitha',
    # common misspellings
    'immediatly',
    'urgnt',
    'meetng',
    # presentation-style queries
    'prepare a quick summary of recent job offers',
]

print('Total emails loaded:', len(load_all_emails()))
for q in queries:
    print('\n=== Query:', q)
    res = search_emails_by_text(q)
    print('Matches:', len(res))
    for m in res:
        print('-', m.get('id'), m.get('subject') or '(no subject)', 'from', m.get('from'))
    # also print a polished per-query summary
    print('\nPolished summary:')
    try:
        print(handle_email_summary.__globals__['summarize_emails_by_query'](q))
    except Exception:
        # fallback if function not available
        print(handle_email_summary()[:800])

print('\nFull email summary (legacy):')
print(handle_email_summary()[:2000])
