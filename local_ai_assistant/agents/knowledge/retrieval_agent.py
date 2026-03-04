import os
import re
import pandas as pd

try:
    import ollama
    HAVE_OLLAMA = True
except Exception:
    ollama = None
    HAVE_OLLAMA = False

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_PATH = os.path.join(ROOT, "data", "documents")


def _list_doc_files():
    if not os.path.exists(DOCS_PATH):
        return []
    return os.listdir(DOCS_PATH)


def _detect_target_file(query: str):
    """Return the specific filename the user is asking about, or None."""
    q = query.strip()
    available = _list_doc_files()

    # 1. Direct substring match against known filenames (case-insensitive)
    q_lower = q.lower()
    for fname in available:
        if fname.lower() in q_lower:
            return fname

    # 2. Regex for any word.ext pattern (handles filenames with spaces via greedy match)
    m = re.search(r"[\w\s\-\.,()]+\.(?:pdf|csv|txt|png|jpg|jpeg|docx|xlsx)", q, flags=re.IGNORECASE)
    if m:
        candidate = m.group(0).strip()
        for fname in available:
            if fname.lower() == candidate.lower():
                return fname
        stem = os.path.splitext(candidate)[0].lower()
        for fname in available:
            if stem in fname.lower():
                return fname

    # 3. Keyword match — split filename into words and check if all appear in query
    #    e.g. "sandeep_internship_work.pdf" has keywords [sandeep, internship, work]
    #    query "what does the internship pdf say" contains "internship" → match
    for fname in available:
        ext = os.path.splitext(fname)[1].lower()
        if ext not in {".pdf", ".csv", ".txt", ".png", ".jpg", ".jpeg", ".docx", ".xlsx"}:
            continue
        stem_words = re.findall(r"[a-z]+", os.path.splitext(fname)[0].lower())
        # Match if any meaningful stem word (len>3) appears in the query
        if any(w in q_lower for w in stem_words if len(w) > 3):
            return fname

    return None


def _load_file_content(fname: str):
    """Load text content from a document file. Returns (text, fname)."""
    fpath = os.path.join(DOCS_PATH, fname)
    if not os.path.exists(fpath):
        return None, None
    ext = os.path.splitext(fname)[1].lower()

    if ext == ".pdf":
        try:
            from langchain_community.document_loaders import PyPDFLoader
            docs = list(PyPDFLoader(fpath).load())
            return "\n\n".join(d.page_content for d in docs), fname
        except Exception as e:
            return f"(Error reading PDF: {e})", fname

    elif ext == ".csv":
        try:
            return pd.read_csv(fpath).to_string(index=False), fname
        except Exception as e:
            return f"(Error reading CSV: {e})", fname

    elif ext == ".txt":
        try:
            return open(fpath, "r", encoding="utf-8", errors="ignore").read(), fname
        except Exception as e:
            return f"(Error reading TXT: {e})", fname

    elif ext in {".png", ".jpg", ".jpeg"}:
        try:
            import pytesseract
            from PIL import Image
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            text = pytesseract.image_to_string(Image.open(fpath)).strip()
            return text or "(Image has no readable text)", fname
        except Exception as e:
            return f"(Error reading image with OCR: {e})", fname

    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(fpath)
            return "\n".join(p.text for p in doc.paragraphs), fname
        except Exception as e:
            return f"(Error reading DOCX: {e})", fname

    return "(Unsupported file type)", fname


def _ask_llm(model_name, context, query, source):
    """Ask Ollama to answer using only the provided context. Returns answer string or None."""
    if not HAVE_OLLAMA:
        return None
    try:
        response = ollama.chat(
            model=model_name,
            options={"temperature": 0.0},
            messages=[
                {"role": "system", "content":
                    "Answer ONLY using the provided CONTEXT from the document. "
                    "Be concise and specific. "
                    "If the answer is not in the context, say 'Not found in document.'"},
                {"role": "user", "content":
                    f"Document: {source}\nContext:\n{context[:3000]}\n\nQuestion: {query}"},
            ],
        )
        answer = response.get("message", {}).get("content", "").strip()
        if answer and not answer.lower().startswith("not found"):
            return answer
    except Exception:
        pass
    return None


def handle_retrieval(query, vector_db, threshold, model_name):
    """
    Answer a document query.

    Rule 1: If the user mentions a specific filename (any extension) →
            load ONLY that file and answer from it exclusively.

    Rule 2: Otherwise → use vector search but return only results from
            the single best-matching source document, never mixing sources.
    """

    # ── Rule 1: specific file mentioned ──────────────────────────────────────
    target_file = _detect_target_file(query)
    if target_file:
        content, source = _load_file_content(target_file)
        if not content:
            return f"Could not read '{target_file}'.", target_file
        answer = _ask_llm(model_name, content, query, source)
        if answer:
            return answer, source
        return content[:2000], source

    # ── Rule 2: vector search, single best source ─────────────────────────────
    if vector_db is None:
        return None, None

    try:
        results = vector_db.similarity_search_with_score(query, k=10)
    except Exception:
        return None, None

    if not results:
        return None, None

    # Pick the source that has the best (lowest) score
    best_score = float("inf")
    best_source = None
    for doc, score in results:
        if score < best_score:
            best_score = score
            best_source = doc.metadata.get("source", "")

    # Keep only chunks from that one source
    filtered = [doc for doc, _ in results if doc.metadata.get("source", "") == best_source]
    if not filtered:
        filtered = [doc for doc, _ in results[:3]]

    context = "\n\n".join(doc.page_content for doc in filtered)
    source = best_source or "Unknown document"

    answer = _ask_llm(model_name, context, query, source)
    if answer:
        return answer, source

    snippet = context if len(context) < 2000 else context[:2000] + "..."
    return snippet, source