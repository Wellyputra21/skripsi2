import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus


NOISE_PATTERN = re.compile(r"[^a-z0-9\s]")


def clean_text(text: str) -> str:
    normalized = text.lower().strip()
    normalized = NOISE_PATTERN.sub(" ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _stable_seed(*parts: str) -> str:
    base = "-".join(clean_text(part) for part in parts if part)
    return re.sub(r"[^a-z0-9-]", "", base.replace(" ", "-")) or "destination-riau"


def build_fallback_images(destination: dict[str, Any], total: int = 3) -> list[str]:
    name = str(destination.get("name", ""))
    category = str(destination.get("category", ""))
    location = str(destination.get("location", ""))
    query = quote_plus(",".join([name, category, location, "riau", "indonesia"]))
    seed = _stable_seed(str(destination.get("id", "")), name, category, location)

    return [
        f"https://source.unsplash.com/1600x900/?{query}&sig={seed}-{index}"
        for index in range(total)
    ]


def normalize_images(destination: dict[str, Any], total: int = 3) -> tuple[list[str], list[str]]:
    raw_images = destination.get("images", [])
    images = [str(url).strip() for url in raw_images if str(url).strip()][:total]
    fallback_images = build_fallback_images(destination, total=total)

    if len(images) < total:
        images.extend(fallback_images[len(images) : total])

    return images, fallback_images


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
        images, fallback_images = normalize_images(row)
        processed_data.append(
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "category": row["category"],
                "location": row["location"],
                "rating": row["rating"],
                "images": images,
                "fallback_images": fallback_images,
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
