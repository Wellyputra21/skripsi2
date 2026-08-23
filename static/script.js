const form = document.getElementById("recommend-form");
const queryInput = document.getElementById("query");
const topNInput = document.getElementById("top_n");
const resultsList = document.getElementById("results");
const resultSummary = document.getElementById("result-summary");
const resultTitle = document.getElementById("result-title");
const locationsToggle = document.getElementById("locations-toggle");
const locationDropdown = document.getElementById("location-dropdown");
const locationGrid = document.getElementById("location-grid");
const featuredList = document.getElementById("featured-list");
const statDestinations = document.getElementById("stat-destinations");
const statLocations = document.getElementById("stat-locations");

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

function scrollToResults() {
  const el = document.getElementById("hasil");
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
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

  const query = queryInput.value.trim();
  const topN = Number(topNInput.value || 5);

  if (!query) {
    return;
  }

  resultTitle.textContent = "Hasil Rekomendasi";
  resultSummary.textContent = "Sedang memproses rekomendasi...";
  resultsList.innerHTML = '<li class="item">Memproses rekomendasi...</li>';

  try {
    const response = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_n: topN }),
    });

    const payload = await response.json();

    if (!response.ok) {
      resultSummary.textContent = "Terjadi error saat memproses.";
      resultsList.innerHTML = `<li class="item">Error: ${payload.error || "Terjadi kesalahan."}</li>`;
      return;
    }

    renderResults(payload.results || [], `${(payload.results || []).length} destinasi paling relevan ditemukan.`);
    scrollToResults();
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
    if (statLocations) statLocations.textContent = String(list.length);

    locationDropdown.innerHTML = "";
    locationGrid.innerHTML = "";
    for (const loc of list) {
      const menuItem = document.createElement("li");
      menuItem.innerHTML = `<button type="button" class="dropdown-item" data-location="${loc}">${loc}</button>`;
      locationDropdown.appendChild(menuItem);

      const cell = document.createElement("li");
      cell.innerHTML = `<button type="button" class="location-btn" data-location="${loc}">${loc}</button>`;
      locationGrid.appendChild(cell);
    }
  } catch (e) {
    locationDropdown.innerHTML = '<li><button type="button" class="dropdown-item">Gagal memuat kabupaten.</button></li>';
  }
}

async function showLocation(location) {
  locationDropdown.classList.remove("open");
  resultTitle.textContent = `Wisata di ${location}`;
  resultSummary.textContent = "Memuat destinasi...";
  resultsList.innerHTML = '<li class="item">Memuat destinasi...</li>';
  try {
    const res = await fetch(`/destinations?location=${encodeURIComponent(location)}`);
    const payload = await res.json();
    const list = payload.results || [];
    renderResults(list, `${list.length} destinasi ditemukan di ${location}.`);
    scrollToResults();
  } catch (e) {
    resultSummary.textContent = "Gagal memuat destinasi.";
    resultsList.innerHTML = '<li class="item">Tidak dapat terhubung ke server.</li>';
  }
}

async function renderFeatured() {
  try {
    const res = await fetch("/destinations");
    const payload = await res.json();
    const all = payload.results || [];
    if (statDestinations) statDestinations.textContent = String(all.length);
    const top = all.slice().sort((a, b) => (b.rating || 0) - (a.rating || 0)).slice(0, 6);

    if (!featuredList) return;
    featuredList.innerHTML = "";
    for (const item of top) {
      const img = (item.images && item.images[0]) || "/static/fallback-destination.svg";
      const li = document.createElement("li");
      li.innerHTML = `
        <a class="featured-card item-link" href="/destination/${item.id}">
          <div class="featured-media">
            <img src="${img}" alt="${item.name}" loading="lazy"
              onerror="this.onerror=null; this.src='/static/fallback-destination.svg';" />
          </div>
          <div class="featured-body">
            <h3>${item.name}</h3>
            <div class="chip-row">
              <span class="chip">${item.category}</span>
              <span class="chip">${item.location}</span>
              <span class="chip">Rating: ${item.rating}</span>
            </div>
          </div>
        </a>
      `;
      featuredList.appendChild(li);
    }
  } catch (e) {
    if (featuredList) {
      featuredList.innerHTML = '<li class="item">Gagal memuat destinasi unggulan.</li>';
    }
  }
}

locationsToggle.addEventListener("click", (event) => {
  event.stopPropagation();
  locationDropdown.classList.toggle("open");
});

locationDropdown.addEventListener("click", (event) => {
  const btn = event.target.closest(".dropdown-item");
  if (!btn) return;
  showLocation(btn.dataset.location);
});

locationGrid.addEventListener("click", (event) => {
  const btn = event.target.closest(".location-btn");
  if (!btn) return;
  showLocation(btn.dataset.location);
});

document.addEventListener("click", () => {
  locationDropdown.classList.remove("open");
});

loadLocations();
renderFeatured();

/* ===== Chatbot UI (tanpa integrasi backend) ===== */
const chatbot = document.querySelector(".chatbot");
const chatbotToggle = document.getElementById("chatbot-toggle");
const chatbotClose = document.getElementById("chatbot-close");
const chatbotForm = document.getElementById("chatbot-form");
const chatbotInput = document.getElementById("chatbot-input");
const chatbotMessages = document.getElementById("chatbot-messages");

function appendChatMessage(role, text) {
  const div = document.createElement("div");
  div.className = "chat-msg " + role;
  div.textContent = text;
  chatbotMessages.appendChild(div);
  chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  return div;
}

function openChatbot() {
  chatbot.classList.add("open");
  if (chatbotInput) chatbotInput.focus();
}

function closeChatbot() {
  chatbot.classList.remove("open");
}

chatbotToggle.addEventListener("click", () => {
  if (chatbot.classList.contains("open")) {
    closeChatbot();
  } else {
    openChatbot();
  }
});

chatbotClose.addEventListener("click", closeChatbot);

let chatbotHistory = [];

chatbotForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = chatbotInput.value.trim();
  if (!text || chatbotForm.classList.contains("busy")) return;

  chatbotHistory.push({ role: "user", content: text });
  appendChatMessage("user", text);
  chatbotInput.value = "";

  const history = chatbotHistory.slice(-10);
  const typingEl = appendChatMessage("bot", "Mengetik...");
  chatbotForm.classList.add("busy");

  try {
    const res = await fetch("/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history }),
    });
    const payload = await res.json();
    typingEl.remove();

    if (!res.ok) {
      chatbotHistory.pop();
      appendChatMessage("bot", "⚠️ " + (payload.error || "Terjadi kesalahan."));
      return;
    }

    appendChatMessage("bot", payload.reply || "...");
    chatbotHistory.push({ role: "assistant", content: payload.reply });
  } catch (error) {
    typingEl.remove();
    chatbotHistory.pop();
    appendChatMessage("bot", "⚠️ Tidak dapat terhubung ke server.");
  } finally {
    chatbotForm.classList.remove("busy");
    chatbotInput.focus();
  }
});
