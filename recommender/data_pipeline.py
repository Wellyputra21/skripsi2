import json
import re
from pathlib import Path
from typing import Any


NOISE_PATTERN = re.compile(r"[^a-z0-9\s]")


def clean_text(text: str) -> str:
    normalized = text.lower().strip()
    normalized = NOISE_PATTERN.sub(" ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def combine_text_fields(destination: dict[str, Any]) -> str:
    composite = " ".join(
        [
            str(destination.get("name", "")),
            str(destination.get("description", "")),
            str(destination.get("category", "")),
            str(destination.get("location", "")),
        ]
    )
    return clean_text(composite)


def preprocess_dataset(raw_path: Path, processed_path: Path) -> list[dict[str, Any]]:
    with raw_path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    processed_data: list[dict[str, Any]] = []
    for row in raw_data:
        text_for_embedding = combine_text_fields(row)
        processed_data.append(
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "location": row["location"],
                "rating": row["rating"],
                "text_for_embedding": text_for_embedding,
            }
        )

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    with processed_path.open("w", encoding="utf-8") as file:
        json.dump(processed_data, file, ensure_ascii=False, indent=2)

    return processed_data


def load_processed_data(processed_path: Path) -> list[dict[str, Any]]:
    with processed_path.open("r", encoding="utf-8") as file:
        return json.load(file)
