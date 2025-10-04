const API_BASE = "http://127.0.0.1:5000";

function getQuery() {
  const v = document.getElementById("vehicleFilter").value;
  const s = document.getElementById("sentimentFilter").value;
  return v || s ? `?vehicle=${v}&sentiment=${s}` : "";
}

function resetChart(id) {
  const old = document.getElementById(id);
  const c = document.createElement("canvas");
  c.id = id;
  old.parentNode.replaceChild(c, old);
}

// KPIs
function loadKPIs() {
  fetch(`${API_BASE}/filter${getQuery()}`)
    .then(r => r.json())
    .then(d => {
      document.getElementById("totalReviews").textContent = `Total Reviews: ${d.total_reviews}`;
      document.getElementById("avgRating").textContent = `Avg Rating: ${d.avg_rating || "--"}`;
      document.getElementById("posRate").textContent = `Positive: ${d.pos_percent}%`;
      document.getElementById("negRate").textContent = `Negative: ${d.neg_percent}%`;
      document.getElementById("growthPotential").textContent = `Sales Growth Potential: ${d.growth_potential}%`;
    });
}

// Sentiment Pie
function loadSentiment() {
  resetChart("sentimentChart");
  fetch(`${API_BASE}/sentiment${getQuery()}`)
    .then(r => r.json())
    .then(d => {
      new Chart(document.getElementById("sentimentChart"), {
        type: "pie",
        data: {
          labels: Object.keys(d),
          datasets: [{ data: Object.values(d), backgroundColor: ["#28a745", "#dc3545", "#ffc107"] }]
        },
        options: { plugins: { legend: { position: "bottom" } } }
      });
    });
}

// Feature Bar
function loadFeature() {
  resetChart("featureChart");
  fetch(`${API_BASE}/features${getQuery()}`)
    .then(r => r.json())
    .then(d => {
      const labels = Object.keys(d.Positive || {});
      new Chart(document.getElementById("featureChart"), {
        type: "bar",
        data: {
          labels,
          datasets: [
            { label: "Positive", data: labels.map(f => d.Positive[f] || 0), backgroundColor: "#28a745" },
            { label: "Negative", data: labels.map(f => d.Negative[f] || 0), backgroundColor: "#dc3545" }
          ]
        },
        options: { responsive: true }
      });
    });
}

// Competitors
function loadCompetitors() {
  resetChart("competitorChart");
  fetch(`${API_BASE}/competitors${getQuery()}`)
    .then(r => r.json())
    .then(d => {
      new Chart(document.getElementById("competitorChart"), {
        type: "bar",
        data: {
          labels: Object.keys(d),
          datasets: [{ label: "Mentions", data: Object.values(d), backgroundColor: "#007bff" }]
        }
      });
    });
}

// Ratings
function loadRatings() {
  resetChart("ratingChart");
  fetch(`${API_BASE}/ratings${getQuery()}`)
    .then(r => r.json())
    .then(d => {
      new Chart(document.getElementById("ratingChart"), {
        type: "bar",
        data: {
          labels: Object.keys(d),
          datasets: [{ label: "Avg Rating", data: Object.values(d), backgroundColor: "#17a2b8" }]
        }
      });
    });
}

// Recommendations
function loadRecs() {
  fetch(`${API_BASE}/recommendations${getQuery()}`)
    .then(r => r.json())
    .then(d => {
      const c = document.getElementById("recContainer");
      c.innerHTML = `
        <h3>Negative Issues</h3>
        ${d.Negative.map(x => `<div class="rec-card negative"><b>${x.issue}</b>: ${x.suggestion}</div>`).join("")}
        <h3>Positive Opportunities</h3>
        ${d.Positive.map(x => `<div class="rec-card positive"><b>${x.opportunity}</b>: ${x.suggestion}</div>`).join("")}
      `;
    });
}

// Summary
function loadSummary() {
  fetch(`${API_BASE}/summary${getQuery()}`)
    .then(r => r.json())
    .then(d => {
      document.getElementById("aiSummary").textContent = d.summary || "No summary available.";
    });
}

function applyFilters() {
  loadKPIs();
  loadSentiment();
  loadFeature();
  loadCompetitors();
  loadRatings();
  loadRecs();
  loadSummary();
}

document.getElementById("applyFiltersBtn").addEventListener("click", applyFilters);
applyFilters();
