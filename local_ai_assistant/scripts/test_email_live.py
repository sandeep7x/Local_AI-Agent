"""Quick test to verify live IMAP fetch, sender filter, and TTL caching."""
import sys, time, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.knowledge.email_summarizer_agent import handle_email_summary, summarize_emails_by_query
from agents.knowledge.email_query_agent import invalidate_email_cache, improved_search_emails

print("=== TEST 1: handle_email_summary (first call = fresh IMAP) ===")
invalidate_email_cache()
t0 = time.time()
out = handle_email_summary()
print(out)
print(f"[TIME] {time.time()-t0:.1f}s\n")

print("=== TEST 2: search 'emergency meeting' (TTL cache — should be fast) ===")
t1 = time.time()
print(summarize_emails_by_query("emergency meeting"))
print(f"[TIME] {time.time()-t1:.1f}s  (should be <1s — uses in-memory cache)\n")

print("=== TEST 3: search 'job' (TTL cache) ===")
t2 = time.time()
print(summarize_emails_by_query("job"))
print(f"[TIME] {time.time()-t2:.1f}s\n")

print("=== TEST 4: sender filter — 'mails from sandeep' ===")
t3 = time.time()
results = improved_search_emails("mails from sandeep")
for r in results:
    print(f"  From: {r.get('from','')} | Subject: {r.get('subject','(no subj)')}")
print(f"[TIME] {time.time()-t3:.1f}s\n")

print("=== TEST 5: sender filter — 'give only sandeep mails' ===")
t4 = time.time()
results = improved_search_emails("give only sandeep mails")
for r in results:
    print(f"  From: {r.get('from','')} | Subject: {r.get('subject','(no subj)')}")
print(f"[TIME] {time.time()-t4:.1f}s\n")

print("=== TEST 6: sender filter — 'susmitha emails' ===")
t5 = time.time()
results = improved_search_emails("susmitha emails")
for r in results:
    print(f"  From: {r.get('from','')} | Subject: {r.get('subject','(no subj)')}")
print(f"[TIME] {time.time()-t5:.1f}s\n")

print("=== TEST 7: combined — 'meeting from susmitha' ===")
t6 = time.time()
results = improved_search_emails("meeting from susmitha")
for r in results:
    print(f"  From: {r.get('from','')} | Subject: {r.get('subject','(no subj)')}")
print(f"[TIME] {time.time()-t6:.1f}s\n")

print("=== TEST 8: force-refresh (simulate second user query with invalidate) ===")
invalidate_email_cache()
t7 = time.time()
results = improved_search_emails("mroads")
for r in results:
    print(f"  From: {r.get('from','')} | Subject: {r.get('subject','(no subj)')}")
print(f"[TIME] {time.time()-t7:.1f}s  (should be ~8s — forced fresh IMAP)\n")

