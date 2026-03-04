# agent_mcp/tools/__init__.py
# Tool wrappers — each module wraps one or more existing agents.
# Import order matches the server registration order.
from agent_mcp.tools.reminders import (
    reminders_set,
    reminders_list,
    reminders_delete,
)
from agent_mcp.tools.emails import (
    email_search,
    email_summarize,
    email_list_all,
)
from agent_mcp.tools.documents import (
    documents_search,
    documents_summarize,
    documents_topics,
    documents_list,
)
from agent_mcp.tools.system import (
    system_chat,
    system_intent,
    system_status,
)

__all__ = [
    # Reminders
    "reminders_set",
    "reminders_list",
    "reminders_delete",
    # Emails
    "email_search",
    "email_summarize",
    "email_list_all",
    # Documents
    "documents_search",
    "documents_summarize",
    "documents_topics",
    "documents_list",
    # System
    "system_chat",
    "system_intent",
    "system_status",
]
