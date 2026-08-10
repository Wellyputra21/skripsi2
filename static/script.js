const form = document.getElementById("recommend-form");
const resultsList = document.getElementById("results");
const resultSummary = document.getElementById("result-summary");
const resultTitle = document.getElementById("result-title");
const locationList = document.getElementById("location-list");

let activeLocation = null;

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

function renderResults(results, summary) {
  resultsList.innerHTML = "";

  if (!results.length) {
    resultSummary.textContent = summary || "0 destinasi ditemukan.";
    resultsList.innerHTML = '<li class="item">Tidak ada destinasi ditemukan.</li>';
    return;
  }

  resultSummary.textContent = summary || `${results.length} destinasi paling relevan ditemukan.`;

  for (const item of results) {
    const li = document.createElement("li");
    li.className = "item";
    const hasScore = typeof item.score === "number";
    const similarityPercent = hasScore
      ? Math.max(0, Math.min(100, ((item.score + 1) / 2) * 100))
      : 0;
    const images = Array.isArray(item.images) ? item.images.slice(0, 3) : [];
    const fallbackImages = Array.isArray(item.fallback_images)
      ? item.fallback_images.slice(0, 3)
      : [];
    const galleryHtml = images.length
      ? `<div class="gallery">${images
          .map(
            (src, i) =>
              `<img src="${src}" alt="${item.name} - gambar ${i + 1}" loading="lazy" referrerpolicy="no-referrer" data-fallback1="${
                fallbackImages[i] || ""
              }" data-fallback2="/static/fallback-destination.svg" onerror="handleImageError(this);" />`
          )
          .join("")}</div>`
      : "";

    const scoreHtml = hasScore
      ? `<div class="score-wrap">
          <div class="score-label">Skor kemiripan: <strong>${item.score.toFixed(4)}</strong></div>
          <div class="score-track"><div class="score-fill" style="width:${similarityPercent.toFixed(1)}%"></div></div>
        </div>`
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
        ${scoreHtml}
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

  setActiveLocation(null);
  resultTitle.textContent = "Hasil Rekomendasi";
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

async function loadLocations() {
  try {
    const res = await fetch("/locations");
    const payload = await res.json();
    const list = payload.locations || [];
    locationList.innerHTML = "";
    for (const loc of list) {
      const li = document.createElement("li");
      li.innerHTML = `<button type="button" class="location-btn" data-location="${loc}">${loc}</button>`;
      locationList.appendChild(li);
    }
  } catch (e) {
    locationList.innerHTML =
      '<li class="location-item">Tidak dapat memuat kabupaten.</li>';
  }
}

function setActiveLocation(location) {
  activeLocation = location;
  locationList.querySelectorAll(".location-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.location === location);
  });
}

async function showLocation(location) {
  setActiveLocation(location);
  resultTitle.textContent = `Wisata di ${location}`;
  resultSummary.textContent = "Memuat destinasi...";
  resultsList.innerHTML = '<li class="item">Memuat destinasi...</li>';
  try {
    const res = await fetch(`/destinations?location=${encodeURIComponent(location)}`);
    const payload = await res.json();
    const list = payload.results || [];
    renderResults(list, `${list.length} destinasi ditemukan di ${location}.`);
  } catch (e) {
    resultSummary.textContent = "Gagal memuat destinasi.";
    resultsList.innerHTML = '<li class="item">Tidak dapat terhubung ke server.</li>';
  }
}

locationList.addEventListener("click", (event) => {
  const btn = event.target.closest(".location-btn");
  if (!btn) return;
  showLocation(btn.dataset.location);
});

loadLocations();
