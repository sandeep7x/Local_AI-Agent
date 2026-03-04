import os
import json
import re
import time
from difflib import SequenceMatcher

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
EMAIL_FILE = os.path.join(_PROJECT_ROOT, "data", "emails.json")
CACHE_FILE = os.path.join(_PROJECT_ROOT, "data", "email_cache.json")

# In-memory TTL cache — avoids double IMAP fetches within the same query
_live_cache: list = []
_live_cache_ts: float = 0.0
_LIVE_CACHE_TTL: float = 10.0  # seconds


def _fetch_live_and_update_cache(force: bool = False) -> list:
    """Fetch latest emails from IMAP, merge into cache file, return all.

    Results are cached in memory for _LIVE_CACHE_TTL seconds so that
    multiple calls within the same query cycle only hit IMAP once.
    Pass force=True to bypass the TTL (e.g. from startup sync).
    """
    global _live_cache, _live_cache_ts

    now = time.time()
    if not force and _live_cache and (now - _live_cache_ts) < _LIVE_CACHE_TTL:
        return _live_cache  # return cached result — no IMAP round-trip

    try:
        import sys
        if _PROJECT_ROOT not in sys.path:
            sys.path.insert(0, _PROJECT_ROOT)

        from agents.tasks.email_agent import EmailAgent
        agent = EmailAgent()
        if not getattr(agent, 'available', True):
            print("[Email] EmailAgent unavailable (check credentials/.env)")
            return _live_cache  # return whatever we had

        live = agent.fetch_recent_emails(last_n=200)
        if live:
            agent.save_to_cache(live)
            _live_cache = live
            _live_cache_ts = time.time()
            return live
        return _live_cache  # IMAP returned nothing - keep previous
    except Exception as _e:
        print(f"[Email] IMAP fetch error: {_e}")
        return _live_cache  # return whatever was cached rather than empty


def load_all_emails():
    """Always fetch live from IMAP, merge with disk cache, deduplicate by ID."""
    emails_map = {}  # id -> email dict, deduped

    # 1. Load static emails.json
    if os.path.exists(EMAIL_FILE):
        try:
            with open(EMAIL_FILE, "r", encoding="utf-8") as f:
                for e in json.load(f):
                    emails_map[str(e.get("id", ""))] = e
        except Exception:
            pass

    # 2. Load cache file
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for e in data.get("emails", []):
                    emails_map[str(e.get("id", ""))] = e
        except Exception:
            pass

    # 3. Fetch live from IMAP — respects the in-memory TTL (default 30s).
    # To force an immediate refresh, call invalidate_email_cache() first.
    for e in _fetch_live_and_update_cache():
        emails_map[str(e.get("id", ""))] = e

    return list(emails_map.values())


def invalidate_email_cache():
    """Force the next load_all_emails() call to do a fresh IMAP fetch."""
    global _live_cache, _live_cache_ts
    _live_cache = []      # wipe stale in-memory data
    _live_cache_ts = 0.0  # reset TTL so next call always hits IMAP


def _similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def improved_search_emails(query, max_results=20):
    """Robust natural-language email search with fuzzy matching.

    Supports:
      - Hard sender filtering: "from sandeep", "sandeep mails", "only susmitha"
      - Topic search: "emergency meeting", "job offer"
      - Combined: "meeting from susmitha", "job mail from kutluri"
    """
    q = (query or "").strip().lower()
    emails = load_all_emails()
    if not q:
        return []

    # ----------------------------------------------------------------
    # STEP 1: Detect a sender filter
    # Patterns handled:
    #   "from sandeep"            →  from_match
    #   "from sandeep only"       →  from_match (trailing "only" ignored)
    #   "sandeep mails/emails"    →  name_before_mail
    #   "only sandeep mails"      →  name_before_mail
    #   "summarize only sandeep mails" → name_before_mail
    # ----------------------------------------------------------------
    sender_filter = None

    # Pattern 1: explicit "from <name>" anywhere in query
    _from_pat = re.search(r"\bfrom\s+([\w\.@\-]+)", q)
    if _from_pat:
        sender_filter = _from_pat.group(1).strip()

    # Pattern 2: "<name> mails/emails" or "only <name> mails/emails"
    # (captures the word immediately before mails/emails that isn't a stopword)
    _SENDER_STOP = {
        "all","my","your","his","her","their","the","a","an","some","any",
        "new","recent","latest","old","unread","sent","received","summarize",
        "get","show","give","list","find","check","read","only","just","me",
        "mail","email","inbox","mails","emails"
    }
    if not sender_filter:
        _name_pat = re.search(r"\b([\w]+)\s+(?:mails?|emails?)\b", q)
        if _name_pat:
            candidate = _name_pat.group(1).strip()
            if candidate not in _SENDER_STOP and len(candidate) > 2:
                sender_filter = candidate

    # Pattern 3: "only <name>" without the word mails — e.g. "show only susmitha"
    if not sender_filter:
        _only_pat = re.search(r"\bonly\s+([\w]+)\b", q)
        if _only_pat:
            candidate = _only_pat.group(1).strip()
            if candidate not in _SENDER_STOP and len(candidate) > 2:
                sender_filter = candidate

    # ----------------------------------------------------------------
    # STEP 2: Apply sender hard-filter if detected
    # ----------------------------------------------------------------
    if sender_filter:
        sf = sender_filter.lower()
        filtered = [e for e in emails
                    if sf in (e.get("from") or "").lower()
                    or _similar(sf, (e.get("from") or "").lower().split("<")[0].strip()) > 0.65]
        # If name matched at least one email, restrict to those; otherwise ignore the filter
        if filtered:
            emails = filtered
            # If the query is purely about the sender (no topic tokens), return top-N sorted by id
            topic_q = re.sub(r"\b(from|only|mails?|emails?|summarize|show|give|list|get|find|all|"\
                             r"recent|latest|new|my|your)\b", "", q).strip()
            topic_q = re.sub(r"\b" + re.escape(sender_filter) + r"\b", "", topic_q).strip()
            if not topic_q or len(topic_q) < 3:
                # Pure sender query — return all their emails, sorted by id descending
                return sorted(emails, key=lambda e: int(str(e.get("id", 0) or 0)), reverse=True)[:max_results]

    # ----------------------------------------------------------------
    # STEP 3: Normal keyword + fuzzy scoring on the (possibly filtered) list
    # ----------------------------------------------------------------
    about_match = re.search(r"\babout\s+(.+)$", q)
    subject_match = re.search(r"\bsubject[:\s]+(.+)$", q)

    scores = []

    _STOP = {
        "the","a","an","is","in","it","of","to","and","or","for",
        "from","my","me","we","all","any","get","do","did","are",
        "was","be","on","at","by","with","that","this","but","not",
        "can","has","have","had","will","what","which","mail","mails",
        "email","emails","inbox","find","show","related","containing",
        "about","send","sent","received","receive","got","regarding",
        "i","please","just","some","there","recent","new","latest",
        "only","give","summarize","summary",
    }
    tokens = [t for t in re.findall(r"\w+", q) if len(t) > 2 and t not in _STOP]
    # Remove the sender name from tokens so it doesn't corrupt topic scoring
    if sender_filter:
        tokens = [t for t in tokens if t != sender_filter.lower()]
    tokens = [t for t in re.findall(r"\w+", q) if len(t) > 2 and t not in _STOP]

    # Synonym expansion — map query words to related terms to check in emails
    _SYNONYMS = {
        "immediate":  ["immediate","urgent","emergency","asap","critical","soon","quickly"],
        "immediately":["immediate","urgent","emergency","asap","critical","soon","quickly"],
        "urgent":     ["urgent","emergency","asap","immediate","critical","important"],
        "emergency":  ["emergency","urgent","critical","immediate","asap"],
        "respond":    ["respond","response","reply","answer","revert"],
        "response":   ["respond","response","reply","answer","revert"],
        "reply":      ["reply","respond","response","answer"],
        "meeting":    ["meeting","meet","conference","call","discussion","sync"],
        "job":        ["job","offer","position","role","employment","work","career","hiring"],
        "interview":  ["interview","interview","screening","candidature","selection"],
    }

    def _expanded_tokens(t):
        """Return the token plus any synonyms for it."""
        return _SYNONYMS.get(t, [t])

    for mail in emails:
        subj = (mail.get("subject") or "").lower()
        body = (mail.get("body") or "").lower()
        frm  = (mail.get("from") or "").lower()

        score = 0.0

        # ---- explicit about:/subject: ----
        target_topic = None
        if about_match:
            target_topic = about_match.group(1).strip()
        elif subject_match:
            target_topic = subject_match.group(1).strip()
        if target_topic:
            tt = target_topic.lower()
            if tt in subj:
                score += 2.0
            elif tt in body:
                score += 1.5
            elif _similar(tt, subj) > 0.7 or _similar(tt, body) > 0.7:
                score += 1.0

        # ---- exact full-query substring in subject/body ----
        if q in subj:
            score += 2.0
        elif q in body:
            score += 1.5

        # ---- token keyword matching (primary signal) ----
        token_hits = 0
        for t in tokens:
            check_terms = _expanded_tokens(t)
            hit_subj = any(term in subj for term in check_terms)
            hit_body = any(term in body for term in check_terms)
            hit_frm  = any(term in frm  for term in check_terms)
            hit_fuzzy = _similar(t, subj) > 0.8

            if hit_subj:
                score += 1.0
                token_hits += 1
            elif hit_body:
                score += 0.6
                token_hits += 1
            elif hit_frm:
                score += 0.4
                token_hits += 1
            elif hit_fuzzy:
                score += 0.5
                token_hits += 1

        # ---- fuzzy similarity of full query: ONLY use when no tokens present ----
        # (avoids irrelevant emails sneaking in via low fuzzy scores)
        if not tokens:
            sim = max(_similar(q, subj), _similar(q, body[:200]), _similar(q, frm))
            score += sim * 1.5

        # If we have tokens and zero token hits, this email is irrelevant — skip it
        if tokens and token_hits == 0:
            continue

        if score > 0:
            scores.append((score, mail))

    # Sort by relevance; no min_score needed — token gate above already filtered noise
    scores.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scores[:5]]



# Backwards-compatible alias
def search_emails_by_text(keyword):
    return improved_search_emails(keyword)