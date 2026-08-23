import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request

from recommender.config import EMBEDDINGS_PATH, PROCESSED_DATA_PATH
from recommender.data_pipeline import load_processed_data, normalize_images
from recommender.recommendation import DestinationRecommender

app = Flask(__name__)
recommender: DestinationRecommender | None = None

ENV_PATH = Path(__file__).resolve().parent / ".env"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


def load_env() -> None:
    """Load KEY=VALUE pairs from .env without requiring python-dotenv."""
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env()


def _destination_catalog() -> str:
    try:
        rows = load_processed_data(PROCESSED_DATA_PATH)
    except Exception:
        return ""
    entries = [
        f"{row.get('name', '')} ({row.get('location', '')}, {row.get('category', '')})"
        for row in rows
        if row.get("name")
    ]
    return "; ".join(entries)


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/destination/<destination_id>")
def destination_detail(destination_id: str) -> str:
    destination = find_destination_by_id(destination_id)
    if destination is None:
        abort(404)
    return render_template("detail.html", destination=destination)


@app.post("/recommend")
def recommend() -> tuple[object, int] | object:
    if recommender is None:
        return jsonify({"error": "Model is not loaded. Build data and restart app."}), 500

    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query", "")).strip()
    top_n = int(payload.get("top_n", 5)) if str(payload.get("top_n", "")).strip() else 5

    if not query:
        return jsonify({"error": "query is required"}), 400

    results = recommender.recommend(query=query, top_n=top_n)
    return jsonify({"query": query, "results": [asdict(row) for row in results]})


def _destination_payload(row: dict) -> dict:
    images, fallback_images = normalize_images(row)
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "category": row["category"],
        "location": row["location"],
        "rating": float(row["rating"]),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "images": images,
        "fallback_images": fallback_images,
    }


@app.get("/locations")
def list_locations():
    rows = load_processed_data(PROCESSED_DATA_PATH)
    locations: list[str] = []
    seen: set[str] = set()
    for row in rows:
        loc = str(row.get("location", "")).strip()
        if loc and loc not in seen:
            seen.add(loc)
            locations.append(loc)
    return jsonify({"locations": locations})


@app.get("/destinations")
def list_destinations():
    location = (request.args.get("location") or "").strip()
    rows = load_processed_data(PROCESSED_DATA_PATH)
    results = []
    for row in rows:
        if location and str(row.get("location", "")).strip().lower() != location.lower():
            continue
        results.append(_destination_payload(row))
    return jsonify({"location": location, "results": results})


@app.post("/chatbot")
def chatbot():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return jsonify({"error": "API key DeepSeek belum diatur di file .env"}), 500

    payload = request.get_json(silent=True) or {}
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "messages is required"}), 400

    catalog = _destination_catalog()
    system_prompt = (
        "Kamu adalah asisten wisata Provinsi Riau, Indonesia, pada Sistem Rekomendasi "
        "Wisata Riau. Jawab dalam Bahasa Indonesia dengan ringkas, ramah, dan informatif. "
        "Berikut data destinasi yang tersedia:"
        f" {catalog or '(data tidak tersedia)'}"
    )

    messages_for_api = [{"role": "system", "content": system_prompt}]
    for msg in messages[-10:]:
        role = msg.get("role")
        content = str(msg.get("content", "")).strip()
        if role in ("user", "assistant") and content:
            messages_for_api.append({"role": role, "content": content})

    body = {
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat").strip(),
        "messages": messages_for_api,
        "temperature": 0.7,
        "max_tokens": 512,
    }

    request_data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "wisata-riau-chatbot/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        return (
            jsonify({"error": f"DeepSeek API error {exc.code}: {detail}"}),
            exc.code or 502,
        )
    except Exception as exc:
        return jsonify({"error": f"Gagal terhubung ke DeepSeek: {exc}"}), 502

    try:
        reply = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return jsonify({"error": "Respons dari DeepSeek tidak valid"}), 502

    return jsonify({"reply": reply})


def init_recommender() -> None:
    global recommender
    if not PROCESSED_DATA_PATH.exists() or not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            "Processed data or embedding file is missing. "
            "Run scripts/preprocess.py then scripts/build_embeddings.py"
        )
    recommender = DestinationRecommender()


def find_destination_by_id(destination_id: str) -> dict | None:
    rows = load_processed_data(PROCESSED_DATA_PATH)

    for row in rows:
        if row.get("id") == destination_id:
            destination = dict(row)
            images, fallback_images = normalize_images(destination)
            destination["images"] = images
            destination["fallback_images"] = fallback_images
            return destination
    return None


if __name__ == "__main__":
    init_recommender()
    app.run(host="0.0.0.0", port=5000, debug=False)
