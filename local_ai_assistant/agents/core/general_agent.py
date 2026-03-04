import ollama


def handle_general(user_input, model_name, temperature: float = 0.7, num_predict: int = 250):

    response = ollama.chat(
        model=model_name,
        options={
            "temperature": temperature,
            "num_predict": num_predict,
        },
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a smart, friendly personal AI assistant (like Siri or Google Assistant) "
                    "running fully offline. You answer conversationally and concisely. "
                    "For simple questions give a short direct answer (1-3 sentences). "
                    "For factual questions be accurate. "
                    "Never say you cannot help — always try your best."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    return response["message"]["content"]
