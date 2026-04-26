from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from recommender.config import PROCESSED_DATA_PATH, RAW_DATA_PATH
from recommender.data_pipeline import preprocess_dataset


if __name__ == "__main__":
    rows = preprocess_dataset(RAW_DATA_PATH, PROCESSED_DATA_PATH)
    print(f"Processed {len(rows)} destination records -> {PROCESSED_DATA_PATH}")
