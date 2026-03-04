"""
mcp/tools/emails.py
===================
MCP tool wrappers for the email subsystem.

Wraps (without modifying):
  • agents/knowledge/email_query_agent.py   → search / load emails
  • agents/knowledge/email_summarizer_agent.py → summarise

Exposed MCP tools
-----------------
  email.search      → natural-language search over inbox
  email.summarize   → summarise the whole inbox or emails matching a query
  email.list_all    → return raw email list (newest first)
"""

from __future__ import annotations

import sys
import os

# ── project root on path ───────────────────────────────────────────────────
_MCP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT    = os.path.dirname(_MCP_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ── existing agents (unchanged) ────────────────────────────────────────────
from agents.knowledge.email_query_agent import (
    improved_search_emails,
    search_emails_by_text,
    load_all_emails,
    invalidate_email_cache,
)
from agents.knowledge.email_summarizer_agent import (
    summarize_emails_by_query,
    handle_email_summary,
)


# ══════════════════════════════════════════════════════════════════════════════
# Tool: email.search
# ══════════════════════════════════════════════════════════════════════════════
def email_search(query: str, max_results: int = 8) -> dict:
    """
    Search the email inbox using a natural-language query.

    Performs semantic + keyword search across subject, body, and sender
    fields.  Results are returned newest-first.

    Parameters
    ----------
    query : str
        Natural-language search query.
        Examples: "invoice from Amazon", "meeting with Sarah", "GitHub alerts"
    max_results : int
        Maximum number of emails to return (default 8, max 50).

    Returns
    -------
    dict
        {
          "success": bool,
          "query": str,
          "total_found": int,
          "summary": str,         # formatted presentation-ready text
          "emails": list[dict]    # raw matched email objects
        }

    Each email dict contains at minimum:
        {"id", "from", "subject", "date", "body"}
    """
    if not query or not query.strip():
        return {
            "success": False,
            "query": query,
            "total_found": 0,
            "summary": "No search query provided.",
            "emails": [],
        }

    max_results = max(1, min(int(max_results), 50))

    # Refresh the live cache before searching so results are up to date
    try:
        invalidate_email_cache()
    except Exception:
        pass

    try:
        # improved_search_emails uses fuzzy + keyword matching
        matches = improved_search_emails(query.strip(), max_results=max_results)
        summary = summarize_emails_by_query(query.strip(), max_results=max_results)
        return {
            "success": True,
            "query": query.strip(),
            "total_found": len(matches),
            "summary": summary,
            "emails": matches,
        }
    except Exception as exc:
        # graceful degradation to lower-level search
        try:
            matches = search_emails_by_text(query.strip())[:max_results]
            lines = [f"- [{m.get('id')}] {m.get('subject','(no subject)')} from {m.get('from','?')}" for m in matches]
            return {
                "success": True,
                "query": query.strip(),
                "total_found": len(matches),
                "summary": "\n".join(lines) if lines else "No matching emails found.",
                "emails": matches,
            }
        except Exception:
            return {
                "success": False,
                "query": query.strip(),
                "total_found": 0,
                "summary": f"Email search failed: {exc}",
                "emails": [],
            }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: email.summarize
# ══════════════════════════════════════════════════════════════════════════════
def email_summarize(query: str = "") -> dict:
    """
    Summarise the inbox.

    When *query* is empty, returns a summary of all available emails.
    When *query* is provided, returns a focused summary of matching emails.

    Parameters
    ----------
    query : str, optional
        If non-empty, filters to emails matching this topic/sender/keyword.
        Leave blank for a full inbox summary.

    Returns
    -------
    dict
        {
          "success": bool,
          "mode": "full" | "filtered",
          "query": str,
          "summary": str    # human-readable multi-line summary
        }
    """
    try:
        invalidate_email_cache()
    except Exception:
        pass

    try:
        if query and query.strip():
            result = summarize_emails_by_query(query.strip(), max_results=10)
            return {
                "success": True,
                "mode": "filtered",
                "query": query.strip(),
                "summary": result,
            }
        else:
            result = handle_email_summary()
            return {
                "success": True,
                "mode": "full",
                "query": "",
                "summary": result,
            }
    except Exception as exc:
        return {
            "success": False,
            "mode": "full" if not (query and query.strip()) else "filtered",
            "query": query.strip() if query else "",
            "summary": f"Email summarisation failed: {exc}",
        }


# ══════════════════════════════════════════════════════════════════════════════
# Tool: email.list_all
# ══════════════════════════════════════════════════════════════════════════════
def email_list_all(limit: int = 20) -> dict:
    """
    Return the most recent emails from the merged inbox cache.

    Parameters
    ----------
    limit : int
        Maximum number of emails to return (default 20, max 200).

    Returns
    -------
    dict
        {
          "success": bool,
          "total": int,
          "emails": list[dict]   # most recent first
        }
    """
    limit = max(1, min(int(limit), 200))
    try:
        invalidate_email_cache()
    except Exception:
        pass

    try:
        emails = load_all_emails()
        # Sort newest first by IMAP id
        try:
            emails = sorted(emails, key=lambda e: int(str(e.get("id", 0) or 0)), reverse=True)
        except Exception:
            pass
        return {
            "success": True,
            "total": len(emails),
            "emails": emails[:limit],
        }
    except Exception as exc:
        return {
            "success": False,
            "total": 0,
            "emails": [],
        }
