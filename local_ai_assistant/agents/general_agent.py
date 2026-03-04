import ollama

MODEL_NAME = "llama3.2:1b"

def handle_general(user_input):

    response = ollama.chat(
        model=MODEL_NAME,
        options={
            "temperature": 0.7,
            "num_predict": 200
        },
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    return response["message"]["content"].strip()
