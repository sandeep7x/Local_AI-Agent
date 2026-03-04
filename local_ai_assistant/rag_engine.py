from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import ollama

# Load PDF
loader = PyPDFLoader("sample.pdf")
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)
texts = text_splitter.split_documents(documents)

# Create embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create vector DB
vector_db = Chroma.from_documents(
    texts,
    embedding_model
)

print("PDF loaded and indexed successfully.\n")

THRESHOLD = 0.65  # similarity threshold

while True:
    query = input("Ask a question (type 'exit' to quit): ")

    if query.lower() == "exit":
        break

    # Get similarity with scores
    results = vector_db.similarity_search_with_score(query, k=3)

    best_score = results[0][1]

    # If score is too high distance (less relevant)
    if best_score > THRESHOLD:
        print("\nAnswer:")
        response = ollama.chat(
            model="phi3",
            messages=[{"role": "user", "content": query}]
        )
        print(response["message"]["content"])
        print("\n" + "-"*50 + "\n")
        continue

    # Otherwise use RAG
    docs = [doc for doc, score in results]
    context = "\n\n".join([doc.page_content for doc in docs])

    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "system",
                "content": "Answer strictly from the provided context. If not found, say it is not in the document."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{query}"
            }
        ]
    )

    print("\nAnswer:")
    print(response["message"]["content"])
    print("\n" + "-"*50 + "\n")
