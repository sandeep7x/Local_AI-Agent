import ollama

MODEL_NAME = "llama3.2:1b"

def handle_retrieval(user_input, vector_db, threshold):

    results = vector_db.similarity_search_with_score(user_input, k=5)

    if not results:
        return "No relevant documents found.", None

    best_score = results[0][1]

    if best_score >= threshold:
        return "Not found in document.", None

    docs = [doc for doc, score in results]
    context = "\n\n".join([doc.page_content for doc in docs])
    source = docs[0].metadata.get("source", "Unknown document")

    response = ollama.chat(
        model=MODEL_NAME,
        options={
            "temperature": 0.0,
            "num_predict": 200
        },
        messages=[
            {
                "role": "system",
                "content": "Answer strictly from the provided context. If not found say 'Not found in document'. Keep answer short."
            },
            {
                "role": "user",
                "content": f"{context}\n\nQuestion: {user_input}"
            }
        ]
    )

    answer = response["message"]["content"].strip()

    return answer, source
