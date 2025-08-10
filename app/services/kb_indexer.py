import os
import json
import faiss
import numpy as np
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import sys

# Add the project root to the Python path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from app.services.embeddings import get_embedding  # Local embeddings

# Paths
KB_DIR = root_dir / "kb"
DATA_DIR = root_dir / "data"
DATA_DIR.mkdir(exist_ok=True)

INDEX_PATH = DATA_DIR / "kb_index.faiss"
META_PATH = DATA_DIR / "kb_meta.json"

CHUNK_SIZE = 500  # words
CHUNK_OVERLAP = 50

def strip_html(text: str) -> str:
    """Convert markdown to plain text without HTML tags."""
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Chunk text into overlapping pieces."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append((start, end, chunk))
        start += size - overlap
    return chunks

def build_index():
    kb_files = list(KB_DIR.glob("*.md"))
    meta = []
    embeddings = []

    for file in kb_files:
        raw_text = file.read_text(encoding="utf-8").strip()
        if not raw_text:
            print(f"Skipping empty file: {file.name}")
            continue
        
        clean_text = strip_html(raw_text)
        chunks = chunk_text(clean_text)

        for start, end, chunk in chunks:
            try:
                embedding = get_embedding(chunk)
                embeddings.append(embedding)
                meta.append({
                    "file": file.name,
                    "start_word": start,
                    "end_word": end,
                    "text": chunk
                })
            except Exception as e:
                print(f"Error embedding chunk from {file.name}: {e}")

    if not embeddings:
        print("No embeddings generated — index not created.")
        return

    # Convert to numpy array
    embeddings_np = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(embeddings_np)

    # Build FAISS index
    dim = embeddings_np.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings_np)

    # Save index & metadata
    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Indexed {len(meta)} chunks from {len(kb_files)} files.")

if __name__ == "__main__":
    print("Knowledge Base Directory:", KB_DIR)
    print("Index Path:", INDEX_PATH)
    print("Meta Path:", META_PATH)
    build_index()
