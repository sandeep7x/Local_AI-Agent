import ollama
from datetime import datetime


def detect_intent(user_input):
    response = ollama.chat(
        model='phi3',
        options={
            "temperature": 0,
            "num_predict": 5
        },
        messages=[
            {
                "role": "system",
                "content": "Classify the intent. Return only one word: email_reply, create_reminder, get_date, or general_chat."
            },
            {"role": "user", "content": user_input}
        ]
    )

    return response['message']['content'].strip().lower()


def handle_email(user_input):
    print("\n--- Email Draft ---")
    print("Subject: Regarding Your Message\n")
    print("Dear Recipient,\n")
    print(user_input)
    print("\nBest regards,\nSandeep")
    print("-------------------\n")


def handle_reminder(user_input):
    print("\n--- Reminder Created ---")
    print("Task:", user_input)
    print("Time: (Extract time manually in next version)")
    print("------------------------\n")


def handle_date():
    today = datetime.now().strftime("%A, %d %B %Y")
    print("\n--- Today's Date ---")
    print(today)
    print("--------------------\n")


def normal_chat(user_input):
    response = ollama.chat(
        model='phi3',
        options={
            "temperature": 0.7,
            "num_predict": 100
        },
        messages=[
            {"role": "user", "content": user_input}
        ]
    )

    print("Assistant:", response['message']['content'])


if __name__ == "__main__":
    print("Local AI Agent Started (Type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Assistant shutting down...")
            break

        intent = detect_intent(user_input)

        if "email" in intent:
            handle_email(user_input)

        elif "reminder" in intent:
            handle_reminder(user_input)

        elif "date" in intent:
            handle_date()

        else:
            normal_chat(user_input)
