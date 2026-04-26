import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


def build_and_save_embeddings(
    model: SentenceTransformer,
    processed_json_path: Path,
    embeddings_path: Path,
) -> np.ndarray:
    with processed_json_path.open("r", encoding="utf-8") as file:
        rows = json.load(file)

    texts = [row["text_for_embedding"] for row in rows]
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(embeddings_path, embeddings)
    return embeddings


def load_embeddings(embeddings_path: Path) -> np.ndarray:
    return np.load(embeddings_path)
