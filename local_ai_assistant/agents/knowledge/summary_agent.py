import ollama

def handle_summary(documents, model_name):

    # Take small portion from each document (balanced sampling)
    collected_text = []

    for doc in documents:
        content = doc.page_content.strip()
        if content:
            collected_text.append(content[:500])  # take first 500 chars per doc

    # Limit total size
    combined_text = "\n\n".join(collected_text[:30])  # limit to 30 docs

    response = ollama.chat(
        model=model_name,
        options={
            "temperature": 0.2,
            "num_predict": 400
        },
        messages=[
            {
                "role": "system",
                "content": "Summarize the key themes across ALL provided documents. Mention different domains if present."
            },
            {
                "role": "user",
                "content": combined_text
            }
        ]
    )

    return response["message"]["content"]