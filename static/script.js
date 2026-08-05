const form = document.getElementById("recommend-form");
const resultsList = document.getElementById("results");
const resultSummary = document.getElementById("result-summary");

function handleImageError(img) {
  const fallback1 = img.getAttribute('data-fallback1');
  const fallback2 = img.getAttribute('data-fallback2');
  
  // Prevent infinite loop
  if (img.dataset.retryCount === undefined) {
    img.dataset.retryCount = 0;
  }
  
  img.dataset.retryCount = parseInt(img.dataset.retryCount) + 1;
  
  // Try fallback1 first (Picsum - more reliable)
  if (img.dataset.retryCount === 1 && fallback1) {
    img.src = fallback1;
    img.onerror = function() { handleImageError(this); };
  }
  // Then try fallback2 (local SVG)
  else if (img.dataset.retryCount === 2 && fallback2) {
    img.src = fallback2;
    img.onerror = null; // Stop retrying
  }
  // Final fallback - show placeholder background
  else {
    img.style.backgroundColor = '#f0f0f0';
    img.style.display = 'flex';
    img.style.alignItems = 'center';
    img.style.justifyContent = 'center';
    img.alt = 'Gambar tidak tersedia';
  }
}

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
              `<img src="${src}" alt="${item.name} - gambar ${index + 1}" loading="lazy" referrerpolicy="no-referrer" data-fallback1="${
                fallbackImages[index] || ""
              }" data-fallback2="/static/fallback-destination.svg" onerror="handleImageError(this);" />`
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
