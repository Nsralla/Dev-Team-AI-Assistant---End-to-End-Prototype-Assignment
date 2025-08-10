import json
import faiss
import numpy as np
from pathlib import Path
import sys
# Add the project root to the Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))
from app.services.embeddings import get_embedding  # Local embeddings

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
INDEX_FILE = DATA_DIR / "kb_index.faiss"
META_FILE = DATA_DIR / "kb_meta.json"

def search_kb(query:str, k:int=5):
    index = faiss.read_index(str(INDEX_FILE))
    meta = json.loads(META_FILE.read_text(encoding="utf-8"))
    
    query_vec = np.array([get_embedding(query)], dtype=np.float32)
    faiss.normalize_L2(query_vec)
    
    scores, idxs = index.search(query_vec, k)
    
    results = []
    for score, idx in zip(scores[0], idxs[0]):
        chunk_meta = meta[idx]
        results.append({
            "file": chunk_meta["file"],
            "score": float(score),
            "text": chunk_meta["text"]
        })
    return results