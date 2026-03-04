def decide_intent(user_input: str) -> str:
    text = user_input.lower()

    # Global summary type questions
    if "summarize all" in text or "all documents" in text:
        return "SUMMARY"

    # Topic grouping type questions
    if "topics" in text or "group" in text or "covered" in text:
        return "TOPIC"

    # Simple greeting shortcut
    if text in ["hi", "hello", "hey"]:
        return "GREETING"

    # Default → retrieval
    return "RETRIEVAL"
