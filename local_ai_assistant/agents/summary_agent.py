import ollama

def handle_summary(documents, model_name):

    # Combine all document content
    all_text = "\n\n".join([doc.page_content for doc in documents])

    # Limit size to avoid overload
    limited_text = all_text[:8000]

    response = ollama.chat(
        model=model_name,
        options={
            "temperature": 0.2,
            "num_predict": 300
        },
        messages=[
            {
                "role": "system",
                "content": "Summarize the overall themes across all documents clearly and concisely."
            },
            {
                "role": "user",
                "content": limited_text
            }
        ]
    )

    return response["message"]["content"]
