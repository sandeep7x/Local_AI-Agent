# rag_engine.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def load_embeddings(model_name="intfloat/e5-small-v2"):
    """
    Loads the embedding model.
    Used during:
      - Vector DB creation
      - Vector DB loading
    """
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"}
    )


def create_vector_db(chunks, persist_directory="data/vector_store"):
    """
    Creates a new Chroma Vector DB from document chunks.
    """
    emb = load_embeddings()

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        persist_directory=persist_directory
    )

    return vector_db


def load_vector_db(persist_directory="data/vector_store"):
    """
    Loads an existing vector DB if it exists.
    """
    emb = load_embeddings()

    return Chroma(
        embedding_function=emb,
        persist_directory=persist_directory
    )


def retrieve_answer(query, vector_db, threshold=1.5):
    """
    Handles retrieval logic:
      - Searches vector db
      - Applies threshold filtering
      - Returns best match + source
    """

    results = vector_db.similarity_search_with_score(query, k=1)

    if not results:
        return None, None

    doc, score = results[0]

    if score > threshold:
        return None, None

    return doc.page_content, doc.metadata.get("source")