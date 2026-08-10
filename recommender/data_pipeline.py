import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import quote


NOISE_PATTERN = re.compile(r"[^a-z0-9\s]")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_ROOT = PROJECT_ROOT / "static" / "images"
SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".jfif", ".avif"}


def clean_text(text: str) -> str:
    normalized = text.lower().strip()
    normalized = NOISE_PATTERN.sub(" ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _stable_seed(*parts: str) -> str:
    base = "-".join(clean_text(part) for part in parts if part)
    return re.sub(r"[^a-z0-9-]", "", base.replace(" ", "-")) or "destination-riau"


def _compact_key(text: str) -> str:
    return clean_text(text).replace(" ", "")


def _to_static_url(path: Path) -> str:
    relative_path = path.relative_to(PROJECT_ROOT).as_posix()
    return "/" + quote(relative_path, safe="/")


def _natural_sort_key(path: Path) -> list[object]:
    return [int(chunk) if chunk.isdigit() else chunk.lower() for chunk in re.split(r"(\d+)", path.name)]


@lru_cache(maxsize=1)
def _image_catalog() -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    if not IMAGE_ROOT.exists():
        return catalog

    for file_path in IMAGE_ROOT.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            continue

        try:
            relative_path = file_path.relative_to(IMAGE_ROOT)
        except ValueError:
            continue

        parts = relative_path.parts
        if len(parts) < 3:
            continue

        location_folder = parts[0]
        destination_folder = parts[1]
        catalog.append(
            {
                "location_folder": location_folder,
                "destination_folder": destination_folder,
                "location_key": _compact_key(location_folder),
                "destination_key": _compact_key(destination_folder),
                "path": file_path,
                "url": _to_static_url(file_path),
            }
        )

    return catalog


def _score_folder(destination: dict[str, Any], entry: dict[str, Any]) -> float:
    destination_name = _compact_key(str(destination.get("name", "")))
    destination_location = _compact_key(str(destination.get("location", "")))
    folder_key = entry["destination_key"]
    location_key = entry["location_key"]

    if not destination_name:
        return 0.0

    score = 0.0
    if location_key and destination_location:
        if location_key == destination_location:
            score += 3.0
        elif location_key in destination_location or destination_location in location_key:
            score += 1.5

    if folder_key == destination_name:
        score += 8.0
    elif folder_key in destination_name or destination_name in folder_key:
        score += 6.0
    else:
        score += SequenceMatcher(None, folder_key, destination_name).ratio() * 5.0

    return score


def resolve_local_images(destination: dict[str, Any]) -> list[str]:
    catalog = _image_catalog()
    if not catalog:
        return []

    best_folder: tuple[str, str] | None = None
    best_score = 0.0
    grouped_paths: dict[tuple[str, str], list[Path]] = {}

    for entry in catalog:
        folder_key = (entry["location_folder"], entry["destination_folder"])
        grouped_paths.setdefault(folder_key, []).append(entry["path"])

        score = _score_folder(destination, entry)
        if score > best_score:
            best_score = score
            best_folder = folder_key

    if best_folder is None or best_score < 4.0:
        return []

    urls = [_to_static_url(path) for path in sorted(grouped_paths[best_folder], key=_natural_sort_key)]
    deduped_urls: list[str] = []
    seen_urls: set[str] = set()
    for url in urls:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        deduped_urls.append(url)
    return deduped_urls


def build_fallback_images(destination: dict[str, Any], total: int = 3) -> list[str]:
    """Build fallback images from local static assets only."""
    # Keep fallback fully local to avoid any dependency on external image providers.
    return ["/static/fallback-destination.svg" for _ in range(total)]


def build_primary_images(destination: dict[str, Any], total: int = 3) -> list[str]:
    """Build primary images from local static assets only.

    If destination has no local image paths, return local fallback asset.
    """
    local_images = resolve_local_images(destination)
    if local_images:
        return local_images
    return ["/static/fallback-destination.svg" for _ in range(total)]


def normalize_images(destination: dict[str, Any], total: int = 3) -> tuple[list[str], list[str]]:
    """Normalize and return images with primary and fallback strategies.
    
    Returns:
        Tuple of (primary_images, fallback_images)
        - primary_images: From local data paths (or local fallback if missing)
        - fallback_images: Local fallback asset only
    """
    raw_images = destination.get("images", [])
    # Get primary images from local data, or discover them from the local image library.
    if raw_images and any(str(url).strip() for url in raw_images):
        primary_images = [str(url).strip() for url in raw_images if str(url).strip()][:total]
    else:
        primary_images = build_primary_images(destination, total=total)
    
    # Always use local fallback images.
    fallback_images = build_fallback_images(destination, total=total)
    
    # Extend primary with fallback if needed
    if len(primary_images) < total:
        primary_images.extend(fallback_images[len(primary_images) : total])

    return primary_images, fallback_images


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
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
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
