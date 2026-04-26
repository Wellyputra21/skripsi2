const form = document.getElementById("recommend-form");
const resultsList = document.getElementById("results");

function renderResults(results) {
  resultsList.innerHTML = "";

  if (!results.length) {
    resultsList.innerHTML = '<li class="item">Tidak ada hasil untuk query tersebut.</li>';
    return;
  }

  for (const item of results) {
    const li = document.createElement("li");
    li.className = "item";
    li.innerHTML = `
      <h3>${item.name}</h3>
      <p>${item.description}</p>
      <p class="meta">
        Kategori: ${item.category} | Lokasi: ${item.location} | Rating: ${item.rating} | Similarity: ${item.score.toFixed(4)}
      </p>
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
      resultsList.innerHTML = `<li class="item">Error: ${payload.error || "Terjadi kesalahan."}</li>`;
      return;
    }

    renderResults(payload.results || []);
  } catch (error) {
    resultsList.innerHTML = '<li class="item">Tidak dapat terhubung ke server.</li>';
  }
});
