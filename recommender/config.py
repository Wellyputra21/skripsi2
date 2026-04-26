from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "destinations_riau.json"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "destinations_processed.json"
EMBEDDINGS_PATH = BASE_DIR / "data" / "processed" / "destinations_embeddings.npy"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_N_DEFAULT = 5
