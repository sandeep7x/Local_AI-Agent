import sys
from pathlib import Path

# Ensure project root on sys.path when running scripts directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.core.planner_agent import decide_intent
from agents.knowledge.retrieval_agent import handle_retrieval
from agents.knowledge.email_query_agent import load_all_emails

# Quick test: try a document-focused question
q = "when will the company expand into robotics?"
print('Planner:', decide_intent(q))

# Try retrieval directly (vector_db may be None; this is a simple smoke test)
try:
    from smart_agent import documents, VECTOR_STORE_PATH, vector_db, vector_ready, EMBEDDING_MODEL, MODEL_NAME, THRESHOLD
    print('vector_ready=', vector_ready)
    ans, src = handle_retrieval(q, vector_db, THRESHOLD, MODEL_NAME)
    print('Retrieval answer:', ans[:800] if ans else None)
    print('Source:', src)
except Exception as e:
    print('Direct retrieval test failed:', e)

# Do a simple search over loaded documents
try:
    hits = []
    for d in documents:
        if 'robot' in (d.page_content or '').lower():
            hits.append((d.metadata.get('source'), (d.page_content or '')[:400]))
    print('Local document hits:', hits)
except Exception as e:
    print('Document scan failed:', e)
