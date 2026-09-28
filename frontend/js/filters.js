/**
 * filters.js — Reads filter panel state and decides which markers to show/hide.
 * Exposes: ParkingFilters.apply(allMarkers, clusterGroup)
 *          ParkingFilters.init(onChangeCallback)
 */

const ParkingFilters = (() => {

  /** Read all checked values for a CSS class selector. */
  function checkedValues(cls) {
    return [...document.querySelectorAll(`.${cls}:checked`)].map(el => el.value.toLowerCase());
  }

  /** Current filter state snapshot. */
  function getState() {
    return {
      types:    checkedValues("f-type"),
      payments: checkedValues("f-payment"),
      features: checkedValues("f-feature"),
      priceMin: parseFloat(document.getElementById("price-min").value),
      priceMax: parseFloat(document.getElementById("price-max").value),
    };
  }

  /**
   * Returns true if the feature's properties pass the current filters.
   */
  function passes(p, state) {
    const type = (p.type || "").toLowerCase();

    // Type filter
    if (!state.types.includes(type)) return false;

    // Price range filter (skip for valet / park_and_ride — they use flat rates)
    if (type !== "valet" && type !== "park_and_ride") {
      const r = parseFloat(p.rate_per_hour);
      if (!isNaN(r)) {
        if (r < state.priceMin || r > state.priceMax) return false;
      }
    }

    // Payment filter — require at least one selected method to match
    if (state.payments.length > 0) {
      const pm = (p.payment_method || "").toLowerCase();
      const anyMatch = state.payments.some(pay => {
        if (pay === "app") {
          // match app / myparking / jomparking / etc.
          return pm.includes("app") || pm.includes("jomparking") || pm.includes("parkmate");
        }
        return pm.includes(pay.toLowerCase());
      });
      if (!anyMatch) return false;
    }

    // Feature filters (each selected feature must be satisfied)
    for (const feat of state.features) {
      if (feat === "ev" && (p.ev_charging || "").toUpperCase() !== "YES") return false;
      if (feat === "oku" && (p.disabled_bays || "").toUpperCase() !== "YES") return false;
      if (feat === "motorcycle" && !p.motorcycle_rate) return false;
      if (feat === "bookable" && (p.is_online_bookable || "").toUpperCase() !== "YES") return false;
    }

    return true;
  }

  /**
   * Show/hide markers based on current filter state.
   * @param {L.Marker[]} allMarkers   – array of all markers
   * @param {L.MarkerClusterGroup} clusterGroup
   * @returns {number} count of visible markers
   */
  function apply(allMarkers, clusterGroup) {
    const state = getState();
    let visible = 0;

    clusterGroup.clearLayers();
    allMarkers.forEach(marker => {
      const p = marker.feature && marker.feature.properties;
      if (p && passes(p, state)) {
        clusterGroup.addLayer(marker);
        visible++;
      }
    });

    return visible;
  }

  /**
   * Wire up all filter controls to call onChange whenever a filter changes.
   * @param {Function} onChange – callback()
   */
  function init(onChange) {
    // Checkboxes
    document.querySelectorAll(".f-type, .f-payment, .f-feature").forEach(el => {
      el.addEventListener("change", onChange);
    });

    // Price sliders — keep min ≤ max
    const minSlider = document.getElementById("price-min");
    const maxSlider = document.getElementById("price-max");
    const minLbl    = document.getElementById("price-min-lbl");
    const maxLbl    = document.getElementById("price-max-lbl");

    minSlider.addEventListener("input", () => {
      if (parseFloat(minSlider.value) > parseFloat(maxSlider.value)) {
        minSlider.value = maxSlider.value;
      }
      minLbl.textContent = minSlider.value;
      onChange();
    });

    maxSlider.addEventListener("input", () => {
      if (parseFloat(maxSlider.value) < parseFloat(minSlider.value)) {
        maxSlider.value = minSlider.value;
      }
      maxLbl.textContent = maxSlider.value;
      onChange();
    });

    // Collapsible section headers
    document.querySelectorAll(".collapsible").forEach(header => {
      header.addEventListener("click", () => {
        const target = document.getElementById(header.dataset.target);
        if (!target) return;
        const hidden = target.style.display === "none";
        target.style.display = hidden ? "" : "none";
        header.classList.toggle("closed", !hidden);
      });
    });

    // Sidebar toggle
    const sidebar = document.getElementById("sidebar");
    const toggle  = document.getElementById("sidebar-toggle");
    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
      toggle.innerHTML = sidebar.classList.contains("collapsed") ? "&#x276F;" : "&#x276E;";
    });
  }

  return { apply, init, getState };
})();
