from sentence_transformers import SentenceTransformer

print("LOADING EMBEDDING MODEL")
# Local model — free
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str):
    """Generate local embedding for text (list[float])."""
    return model.encode(text, convert_to_numpy=True).tolist()
