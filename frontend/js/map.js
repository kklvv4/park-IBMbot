/**
 * map.js — Initialises the Leaflet map, loads data from the API,
 *          and wires up search, filters, and stats.
 */

(async () => {

  // ── Map setup ──────────────────────────────────────────────────────────────
  const MAP_CENTER = [3.1390, 101.6869];   // KL city centre
  const MAP_ZOOM   = 11;
  const KL_BOUNDS  = L.latLngBounds(
    L.latLng(2.700, 101.300),              // SW – south Sepang
    L.latLng(3.450, 102.000),              // NE – north Rawang
  );

  const map = L.map("map", {
    center: MAP_CENTER,
    zoom:   MAP_ZOOM,
    maxBounds: KL_BOUNDS,
    maxBoundsViscosity: 0.85,
    zoomControl: true,
  });

  // OpenStreetMap tiles (free, no API key)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map);

  // ── MarkerCluster layer ────────────────────────────────────────────────────
  const clusterGroup = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 50,
    iconCreateFunction(cluster) {
      const count = cluster.getChildCount();
      const size  = count < 10 ? 34 : count < 50 ? 40 : 48;
      return L.divIcon({
        html: `<div style="
          width:${size}px;height:${size}px;
          background:var(--accent);color:#fff;
          border-radius:50%;display:flex;align-items:center;justify-content:center;
          font-weight:700;font-size:${size < 40 ? 12 : 13}px;
          border:2px solid rgba(255,255,255,0.7);
          box-shadow:0 2px 6px rgba(0,0,0,0.3);">${count}</div>`,
        className: "",
        iconSize: [size, size],
      });
    },
  });
  map.addLayer(clusterGroup);

  // ── Loading overlay ────────────────────────────────────────────────────────
  const overlay = document.getElementById("loading-overlay");
  const statCount = document.getElementById("stat-count");
  const statAvg   = document.getElementById("stat-avg");

  /** Update the stats bar. */
  function updateStats(visibleCount, allMarkers) {
    let sum = 0, rateCount = 0;
    allMarkers.forEach(m => {
      const r = m.feature && parseFloat(m.feature.properties.rate_per_hour);
      if (!isNaN(r) && r > 0) { sum += r; rateCount++; }
    });
    const avg = rateCount ? (sum / rateCount).toFixed(2) : null;
    statCount.textContent = `${visibleCount} location${visibleCount !== 1 ? "s" : ""}`;
    statAvg.textContent   = avg ? `avg RM${avg}/hr` : "avg —";
  }

  // ── Load data ──────────────────────────────────────────────────────────────
  let allMarkers = [];

  try {
    const geojson = await ParkingAPI.getAll({
      include_valet: true,
      include_airport: true,
    });

    allMarkers = ParkingMarkers.addFeatures(geojson, clusterGroup);

    overlay.classList.add("hidden");
    updateStats(allMarkers.length, allMarkers);
  } catch (err) {
    overlay.innerHTML = `<p style="color:#dc2626">⚠ Could not load parking data.<br><small>${err.message}</small></p>`;
    console.error(err);
  }

  // ── Filters ────────────────────────────────────────────────────────────────
  ParkingFilters.init(() => {
    const visible = ParkingFilters.apply(allMarkers, clusterGroup);
    updateStats(visible, allMarkers);
  });

  // ── Nominatim search ───────────────────────────────────────────────────────
  const searchInput   = document.getElementById("search-input");
  const searchBtn     = document.getElementById("search-btn");
  const searchResults = document.getElementById("search-results");

  let searchTimeout = null;

  async function doSearch(query) {
    if (!query.trim()) { searchResults.hidden = true; return; }

    // Rate-limit to avoid hammering Nominatim
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      try {
        const url = `https://nominatim.openstreetmap.org/search?` +
          `q=${encodeURIComponent(query + ", Kuala Lumpur OR Selangor, Malaysia")}&` +
          `format=json&addressdetails=1&limit=6&countrycodes=my`;

        const res  = await fetch(url, {
          headers: { "Accept-Language": "en", "User-Agent": "MalaysiaParkingMap/1.0" },
        });
        const data = await res.json();

        searchResults.innerHTML = "";
        if (!data.length) {
          searchResults.innerHTML = `<li style="color:var(--muted);cursor:default">No results found</li>`;
          searchResults.hidden = false;
          return;
        }

        data.forEach(item => {
          const li = document.createElement("li");
          li.textContent = item.display_name;
          li.addEventListener("click", () => {
            map.setView([parseFloat(item.lat), parseFloat(item.lon)], 15);
            searchResults.hidden = true;
            searchInput.value = "";
          });
          searchResults.appendChild(li);
        });
        searchResults.hidden = false;
      } catch (e) {
        console.warn("Nominatim search error:", e);
      }
    }, 500);
  }

  searchBtn.addEventListener("click", () => doSearch(searchInput.value));
  searchInput.addEventListener("keydown", e => {
    if (e.key === "Enter") doSearch(searchInput.value);
  });
  searchInput.addEventListener("input", () => doSearch(searchInput.value));

  // Close search results on map click
  map.on("click", () => { searchResults.hidden = true; });

  // Close on outside click
  document.addEventListener("click", e => {
    if (!e.target.closest("#search-box") && !e.target.closest("#search-results")) {
      searchResults.hidden = true;
    }
  });

  // ── Detail panel close ─────────────────────────────────────────────────────
  document.getElementById("detail-close").addEventListener("click", () => {
    document.getElementById("detail-panel").hidden = true;
  });

})();
