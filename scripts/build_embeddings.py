from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sentence_transformers import SentenceTransformer

from recommender.config import EMBEDDINGS_PATH, MODEL_NAME, PROCESSED_DATA_PATH
from recommender.embedding_store import build_and_save_embeddings


if __name__ == "__main__":
    model = SentenceTransformer(MODEL_NAME)
    embeddings = build_and_save_embeddings(model, PROCESSED_DATA_PATH, EMBEDDINGS_PATH)
    print(f"Saved embeddings shape={embeddings.shape} -> {EMBEDDINGS_PATH}")
