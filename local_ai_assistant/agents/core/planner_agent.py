# agents/core/planner_agent.py
#
# Intent classification using the local LLM (ollama) so the assistant
# understands natural language instead of only rigid keyword commands.
# Regex fast-paths are kept for the most obvious unambiguous patterns
# (greetings, current time/date) to avoid unnecessary LLM calls.

import re

try:
    import ollama as _ollama
    _HAVE_OLLAMA = True
except Exception:
    _ollama = None
    _HAVE_OLLAMA = False

_MODEL = "llama3.2:1b"

_SYSTEM_PROMPT = """You are an intent classifier for a personal AI assistant.
Classify the user message into EXACTLY ONE of these intents (output only the label, nothing else):

GREETING       - hello, hi, how are you, good morning, etc.
TIME           - asking for the current time
DATE           - asking for today's or tomorrow's date
REMINDER_SET   - setting / creating / adding a reminder or alarm
REMINDER_LIST  - listing, showing, or checking reminders
REMINDER_DELETE- deleting or removing a reminder
EMAIL_SUMMARY  - summarising all emails / inbox summary
EMAIL_SEARCH   - searching, finding, filtering, or asking about specific emails or mail
DOCUMENT_LIST  - listing available documents or files
SUMMARY        - summarising or giving an overview of one or more documents
TOPIC          - asking what topics or themes are in the documents
RETRIEVAL      - asking a specific question whose answer may be in local documents (PDFs, CSVs, images)
COMPARE        - comparing two things (vs, better, pros and cons, difference)
CHAT           - purely conversational message that does NOT require documents (jokes, opinions, general knowledge, how are you)
GENERAL        - anything else / unclear

Rules:
- If the message mentions "email", "mail", "inbox", "sender", "received", "sent" → EMAIL_SEARCH or EMAIL_SUMMARY
- If the message asks to be reminded, notified, alerted, or to set an alarm → REMINDER_SET
- If the message asks about content inside documents (PDF, CSV, internship, company data, etc.) → RETRIEVAL or SUMMARY
- If the message asks a factual question about "the company", employees, revenue, products, plans, expansion, etc. → RETRIEVAL
- If the message asks "when will", "when did", "how many", "what year", "who is", "what is the" about a specific entity/fact → RETRIEVAL
- If the message is pure small-talk or conversational with no document/email/reminder context → CHAT
- When in doubt between RETRIEVAL and GENERAL, prefer RETRIEVAL for factual questions.
- Output ONLY the intent label. No explanation. No punctuation."""


def _llm_classify(user_input: str) -> str:
    """Ask the local LLM to classify intent. Returns intent string."""
    try:
        resp = _ollama.chat(
            model=_MODEL,
            options={"temperature": 0.0, "num_predict": 10},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )
        raw = resp.get("message", {}).get("content", "").strip().upper()
        # Extract first word (the label)
        label = re.split(r"[\s\n\r\.,\-]+", raw)[0]
        valid = {
            "GREETING", "TIME", "DATE",
            "REMINDER_SET", "REMINDER_LIST", "REMINDER_DELETE",
            "EMAIL_SUMMARY", "EMAIL_SEARCH",
            "DOCUMENT_LIST", "SUMMARY", "TOPIC", "RETRIEVAL",
            "COMPARE", "CHAT", "GENERAL",
        }
        return label if label in valid else "GENERAL"
    except Exception:
        return None  # signal caller to use regex fallback


def _regex_fastpath(text: str):
    """Quick regex classification for unambiguous patterns. Returns intent or None."""

    # ---- Greetings (fast-path, very clear) ----
    if re.search(r"^(hi+|hello|hey|howdy|good\s*(morning|afternoon|evening|night))[\s!,.*]*$", text):
        return "GREETING"

    # ---- Pure conversational queries that have nothing to do with docs ----
    if re.search(
        r"^(how are you|how do you do|how'?s it going|what'?s up|are you (ok|okay|fine|good|there)|"
        r"do you (think|feel|know|understand)|can you (help|talk|chat)|"
        r"tell me a (joke|story|fact)|give me a (joke|tip|fun fact)|"
        r"what (do you think|is your (name|purpose|function))|"
        r"who are you|what can you do)[\s!?.]*$",
        text,
    ):
        return "CHAT"

    # ---- General knowledge / definition questions → CHAT ----
    # e.g. "what is RAG", "where is india", "how does TCP work", "explain machine learning"
    # These must NOT involve company/document-specific keywords, otherwise fall through to RETRIEVAL.
    _DOC_KEYWORDS = re.compile(
        r"\b(the company|our company|company|revenue|employee|employees|internship|product launch|"
        r"expansion|strategy|goals?|budget|plan|milestone|robotics|office|team|founder|ceo|"
        r"the (document|file|pdf|csv|report|data))\b"
    )
    if re.search(
        r"^(what (is|are|was|were)|where (is|are|was|were)|who (is|are|was|were)|"
        r"how (does|do|did|is|are)|why (is|are|was|were|did|does)|"
        r"explain |define |what does .+ (mean|stand for))",
        text,
    ):
        if not _DOC_KEYWORDS.search(text) and not re.search(r"\.(pdf|csv|docx?|xlsx?|txt|png|jpg|jpeg)\b", text):
            return "CHAT"

    # ---- Document / file-content queries → always RETRIEVAL ----
    # Matches queries that mention a file by extension OR use "mentioned in"/"according to"
    # OR ask "how many/much/long" about something (counts, durations, numbers in docs).
    if re.search(r"\.(pdf|csv|docx?|xlsx?|txt|png|jpg|jpeg)\b", text):
        return "RETRIEVAL"
    if re.search(r"\b(mentioned in|found in|written in|stated in|says in|listed in|according to|in the (document|file|pdf|csv|report|internship))\b", text):
        return "RETRIEVAL"
    if re.search(
        r"\b(how many|how much|how long|how old|what (is|are|was|were) the (name|person|company|organization|role|duration|location|number|date|year|tech|technolog|tool))\b",
        text,
    ):
        # Only route to RETRIEVAL if the query contains at least one content word
        # (avoid routing "what is your name" → RETRIEVAL)
        if not re.search(r"\b(your|you|yourself)\b", text):
            return "RETRIEVAL"

    # ---- Company / business factual questions → RETRIEVAL ----
    # e.g. "when will the company expand into robotics", "how many employees", "company revenue"
    if re.search(r"\b(the company|our company|company'?s?|organisation|organization|the team|the business)\b", text):
        return "RETRIEVAL"

    # ---- Temporal factual questions → RETRIEVAL ----
    # e.g. "when will X happen", "when did X", "what year will", "when is the product launch"
    if re.search(r"\b(when (will|did|does|can|should|would)|what year|which year|when is|when was)\b", text):
        if not re.search(r"\b(you|your|yourself|time)\b", text):
            return "RETRIEVAL"

    # ---- General factual "tell me about X" / "who is X" → RETRIEVAL ----
    if re.search(r"\b(tell me about|what do you know about|information on|details (about|on)|facts (about|on)|who is|what is the (plan|goal|target|strategy|vision|mission|revenue|budget|status|progress|result|outcome))\b", text):
        if not re.search(r"\b(yourself|you)\b", text):
            return "RETRIEVAL"

    # ---- Time / date (fast-path) ----
    if re.search(r"\b(what|current|tell me the|show me the)\b.*(time)\b", text):
        return "TIME"
    if re.search(r"\b(what|current|today.?s?|tell me the)\b.*(date|day)\b", text):
        return "DATE"
    if text in ("time", "date", "what time", "what date", "today"):
        return "TIME" if "time" in text else "DATE"

    # ---- Reminders ----
    if re.search(r"\b(remind|reminder|alarm|alert|notify me|set a reminder)\b", text):
        if re.search(r"\b(list|show|what|display|check|upcoming|pending)\b", text):
            return "REMINDER_LIST"
        if re.search(r"\b(delete|remove|cancel|clear)\b", text):
            return "REMINDER_DELETE"
        return "REMINDER_SET"

    # ---- Email ----
    if re.search(r"\b(email|emails|mail|mails|inbox|sent|received)\b", text):
        if re.search(r"\b(summar|overview|all emails|all mails|latest|recent|refresh|show all|list all)\b", text):
            return "EMAIL_SUMMARY"
        return "EMAIL_SEARCH"

    # ---- Document listing ----
    if re.search(r"\b(list|show|what|display)\b.*\b(documents?|files?)\b", text):
        return "DOCUMENT_LIST"

    # ---- Summarise ----
    if re.search(r"\b(summar|overview|brief|recap)\b", text):
        if re.search(r"\b(email|mail|inbox|mails|emails)\b", text):
            return "EMAIL_SUMMARY"
        return "SUMMARY"

    # ---- Topics ----
    if re.search(r"\b(topics?|themes?|subjects?|key points?)\b", text):
        return "TOPIC"

    # ---- Compare ----
    if re.search(r"\b(vs\.?|versus|compare|better than|pros and cons|difference between|which is (better|best|faster|easier))\b", text):
        return "COMPARE"

    return None  # no fast-path match → use LLM


def decide_intent(user_input: str) -> str:
    text = user_input.strip().lower()

    # 1. Try unambiguous regex fast-path first (instant)
    fast = _regex_fastpath(text)
    if fast:
        return fast

    # 2. Use LLM for everything else (handles all natural language)
    if _HAVE_OLLAMA:
        result = _llm_classify(user_input)
        if result:
            return result

    # 3. Fallback regex rules if LLM unavailable
    if re.search(r"\b(what is|who is|where is|explain|tell me about|describe|when will|when did|how many|the company)\b", text):
        if not re.search(r"\b(your|you|yourself)\b", text):
            return "RETRIEVAL"
    return "GENERAL"