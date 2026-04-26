# Sistem Rekomendasi Wisata Riau (Sentence-BERT)

Implementasi roadmap end-to-end:
- input query user
- semantic recommendation berbasis embedding Sentence-BERT
- cosine similarity untuk ranking Top-N
- backend Flask dengan endpoint POST /recommend
- frontend web lokal (HTML/CSS/JS)

## Arsitektur
Frontend (web) -> Flask API -> Sentence-BERT -> Cosine Similarity -> Top-N destinasi

## Struktur Data
- Raw data: `data/raw/destinations_riau.json`
- Processed data: `data/processed/destinations_processed.json`
- Embedding: `data/processed/destinations_embeddings.npy`

## Setup dan Menjalankan
1. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
2. Preprocessing data:
   ```bash
   python scripts/preprocess.py
   ```
3. Build embedding (offline process):
   ```bash
   python scripts/build_embeddings.py
   ```
4. Jalankan backend + frontend lokal:
   ```bash
   python app.py
   ```
5. Buka browser:
   ```
   http://localhost:5000
   ```

## API
- Endpoint: `POST /recommend`
- Request:
  ```json
  {
    "query": "pantai untuk keluarga",
    "top_n": 5
  }
  ```
- Response:
  ```json
  {
    "query": "pantai untuk keluarga",
    "results": [
      {
        "id": "riau-001",
        "name": "Pantai Rupat Utara",
        "description": "...",
        "category": "pantai",
        "location": "Bengkalis",
        "rating": 4.6,
        "score": 0.8123
      }
    ]
  }
  ```
