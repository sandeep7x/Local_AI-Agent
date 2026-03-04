import os

def list_all_documents(base_path="data/documents"):
    if not os.path.exists(base_path):
        return "No documents folder found."

    files = os.listdir(base_path)
    if not files:
        return "No documents found."

    result = []
    for f in files:
        result.append(f"• {f}")

    return "Here are your documents:\n" + "\n".join(result)