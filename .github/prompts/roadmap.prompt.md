---
name: roadmap
description: Describe when to use this prompt
---
Topiknya menarik, tapi judulmu masih agak “ngambang” secara teknis—**“pre-trained models” itu luas banget**. Kalau tidak dipersempit (misalnya NLP, embedding, atau recommender berbasis deep learning), nanti roadmap-mu bisa terlihat kurang fokus saat sidang. Jadi di roadmap ini sekalian aku arahkan biar lebih tajam dan realistis untuk skripsi.

---

Berikut **roadmap sistem (end-to-end, ringkas, fokus teknis)** dari nol sampai jalan lokal via web:

---

# 🗺️ ROADMAP SISTEM

## 1. Requirement & Arsitektur

* Definisikan:

  * Input: query/preferensi user
  * Output: Top-N destinasi
* Metode: semantic recommendation (embedding + similarity)
* Model: Sentence-BERT
* Rancang arsitektur: Frontend → API → Model → Similarity → Output

---

## 2. Akuisisi & Struktur Data

* Kumpulkan data destinasi Riau
* Field: nama, deskripsi, kategori, lokasi, rating
* Simpan: CSV/JSON

---

## 3. Preprocessing

* Cleaning teks (lowercase, hapus noise)
* Normalisasi
* Gabungkan field → 1 kolom teks

---

## 4. Embedding (Offline Process)

* Load Sentence-BERT
* Encode seluruh data → vector
* Simpan embedding (.npy / pickle / DB)

---

## 5. Indexing & Similarity Engine

* Siapkan matrix embedding
* Implementasi cosine similarity
* Fungsi:

  * input query → encode
  * hitung similarity
  * ranking → Top-N

---

## 6. Storage Layer

* Data: JSON / SQLite
* Embedding: file atau database
* Mapping id ↔ data destinasi

---

## 7. Backend API

* Framework: Flask / FastAPI
* Endpoint:

  * `POST /recommend`
* Load model + embedding saat start
* Return hasil (JSON)

---

## 8. Frontend Web

* HTML + CSS + JavaScript
* Komponen:

  * search input
  * tombol submit
  * list hasil rekomendasi

---

## 9. Integrasi

* Frontend kirim request ke API
* API proses → kirim hasil
* Tampilkan di web

---

## 10. Local Deployment

* Jalankan backend (`python app.py`)
* Akses: `http://localhost:5000`
* Pastikan end-to-end berjalan

---

## 11. Testing & Validasi

* Uji berbagai query
* Cek relevansi hasil
* Debug error

---

## 12. Optimasi (Opsional)

* Simpan cache hasil
* Tambah filter (kategori/lokasi)
* Bandingkan metode (TF-IDF vs embedding)

---

# 🎯 OUTPUT AKHIR

Sistem web lokal:

* user input query
* diproses model pre-trained
* menghasilkan rekomendasi destinasi wisata Riau

