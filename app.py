from dataclasses import asdict

from flask import Flask, abort, jsonify, render_template, request

from recommender.config import EMBEDDINGS_PATH, PROCESSED_DATA_PATH
from recommender.data_pipeline import normalize_images
from recommender.recommendation import DestinationRecommender

app = Flask(__name__)
recommender: DestinationRecommender | None = None


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


def init_recommender() -> None:
    global recommender
    if not PROCESSED_DATA_PATH.exists() or not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            "Processed data or embedding file is missing. "
            "Run scripts/preprocess.py then scripts/build_embeddings.py"
        )
    recommender = DestinationRecommender()


def find_destination_by_id(destination_id: str) -> dict | None:
    if recommender is None:
        return None

    for row in recommender.data:
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
