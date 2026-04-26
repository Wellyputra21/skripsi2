const form = document.getElementById("recommend-form");
const resultsList = document.getElementById("results");
const resultSummary = document.getElementById("result-summary");

function renderResults(results) {
  resultsList.innerHTML = "";

  if (!results.length) {
    resultSummary.textContent = "0 destinasi ditemukan.";
    resultsList.innerHTML = '<li class="item">Tidak ada hasil untuk query tersebut.</li>';
    return;
  }

  resultSummary.textContent = `${results.length} destinasi paling relevan ditemukan.`;

  for (const item of results) {
    const li = document.createElement("li");
    li.className = "item";
    const similarityPercent = Math.max(0, Math.min(100, ((item.score + 1) / 2) * 100));
    const images = Array.isArray(item.images) ? item.images.slice(0, 3) : [];
    const fallbackImages = Array.isArray(item.fallback_images)
      ? item.fallback_images.slice(0, 3)
      : [];
    const galleryHtml = images.length
      ? `<div class="gallery">${images
          .map(
            (src, index) =>
              `<img src="${src}" alt="${item.name} - gambar ${index + 1}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='${
                fallbackImages[index] || "/static/fallback-destination.svg"
              }';" />`
          )
          .join("")}</div>`
      : "";

    li.innerHTML = `
      <a class="item-link" href="/destination/${item.id}">
        <h3>${item.name}</h3>
        <p>${item.description}</p>
        ${galleryHtml}
        <div class="chip-row">
          <span class="chip">Kategori: ${item.category}</span>
          <span class="chip">Lokasi: ${item.location}</span>
          <span class="chip">Rating: ${item.rating}</span>
        </div>
        <div class="score-wrap">
          <div class="score-label">Skor kemiripan: <strong>${item.score.toFixed(4)}</strong></div>
          <div class="score-track"><div class="score-fill" style="width:${similarityPercent.toFixed(1)}%"></div></div>
        </div>
      </a>
    `;
    resultsList.appendChild(li);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = document.getElementById("query").value.trim();
  const topN = Number(document.getElementById("top_n").value || 5);

  if (!query) {
    return;
  }

  resultSummary.textContent = "Sedang memproses rekomendasi...";
  resultsList.innerHTML = '<li class="item">Memproses rekomendasi...</li>';

  try {
    const response = await fetch("/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, top_n: topN }),
    });

    const payload = await response.json();

    if (!response.ok) {
      resultSummary.textContent = "Terjadi error saat memproses.";
      resultsList.innerHTML = `<li class="item">Error: ${payload.error || "Terjadi kesalahan."}</li>`;
      return;
    }

    renderResults(payload.results || []);
  } catch (error) {
    resultSummary.textContent = "Gagal terhubung ke server.";
    resultsList.innerHTML = '<li class="item">Tidak dapat terhubung ke server.</li>';
  }
});
