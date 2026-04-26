from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

from recommender.config import EMBEDDINGS_PATH, MODEL_NAME, PROCESSED_DATA_PATH, TOP_N_DEFAULT
from recommender.data_pipeline import clean_text, load_processed_data, normalize_images
from recommender.embedding_store import load_embeddings


@dataclass
class DestinationResult:
    id: str
    name: str
    description: str
    category: str
    location: str
    rating: float
    images: list[str]
    fallback_images: list[str]
    score: float


class DestinationRecommender:
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self.model = SentenceTransformer(model_name)
        self.data = load_processed_data(PROCESSED_DATA_PATH)
        self.embeddings = load_embeddings(EMBEDDINGS_PATH)

    def recommend(self, query: str, top_n: int = TOP_N_DEFAULT) -> list[DestinationResult]:
        cleaned_query = clean_text(query)
        if not cleaned_query:
            return []

        query_embedding = self.model.encode(
            [cleaned_query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]

        # Cosine similarity with normalized vectors is equivalent to dot product.
        similarity_scores = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarity_scores)[::-1][:top_n]

        recommendations: list[DestinationResult] = []
        for index in top_indices:
            row = self.data[index]
            images, fallback_images = normalize_images(row)
            recommendations.append(
                DestinationResult(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    category=row["category"],
                    location=row["location"],
                    rating=float(row["rating"]),
                    images=images,
                    fallback_images=fallback_images,
                    score=float(similarity_scores[index]),
                )
            )
        return recommendations
