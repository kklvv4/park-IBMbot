/**
 * popup.js — Builds Leaflet popup HTML from a GeoJSON feature's properties.
 * Exposes: ParkingPopup.build(props)
 */

const ParkingPopup = (() => {

  /**
   * Returns the CSS badge colour for a given parking type.
   */
  function typeColor(type) {
    const t = (type || "").toLowerCase();
    if (t === "valet")         return "var(--c-valet)";
    if (t === "park_and_ride") return "var(--c-pr)";
    if (t === "airport")       return "#0369a1";
    if (t === "mall")          return "#7c3aed";
    if (t === "street")        return "#16a34a";
    return "var(--c-mid)";
  }

  /**
   * Human-readable label for type value.
   */
  function typeLabel(type) {
    const map = {
      street: "Street",
      mall: "Mall",
      multistorey: "Multi-Storey",
      open_lot: "Open Lot",
      valet: "Valet",
      park_and_ride: "Park & Ride",
      airport: "Airport",
    };
    return map[(type || "").toLowerCase()] || type || "—";
  }

  /**
   * Format a RM value.
   */
  function rm(val) {
    if (val === null || val === undefined || val === "") return "—";
    const n = parseFloat(val);
    return isNaN(n) ? "—" : `RM ${n.toFixed(2)}`;
  }

  /**
   * Row helper.
   */
  function row(label, value) {
    if (!value || value === "—") return "";
    return `<div class="popup-row">
      <span class="popup-label">${label}</span>
      <span class="popup-value">${value}</span>
    </div>`;
  }

  /**
   * Builds the popup HTML string.
   * @param {object} p  – properties from GeoJSON feature
   */
  function build(p) {
    const rateDisplay = p.type === "valet"
      ? (p.valet_rate ? `RM ${parseFloat(p.valet_rate).toFixed(0)} flat` : "—")
      : rm(p.rate_per_hour) + (p.rate_per_hour ? "/hr" : "");

    const firstHrFree = (p.first_hour_free || "").toUpperCase() === "YES";
    const evOk   = (p.ev_charging   || "").toUpperCase() === "YES";
    const okuOk  = (p.disabled_bays || "").toUpperCase() === "YES";
    const bookOk = (p.is_online_bookable || "").toUpperCase() === "YES";

    const badges = [
      evOk   ? `<span title="EV Charging">⚡ EV</span>` : "",
      okuOk  ? `<span title="OKU Bays">♿ OKU</span>`  : "",
      bookOk ? `<span title="Online Bookable">📱 Online</span>` : "",
      firstHrFree ? `<span>1st hr free</span>` : "",
    ].filter(Boolean).join(" ");

    const sourceLink = p.source_url
      ? `<a class="popup-link" href="${p.source_url}" target="_blank" rel="noopener">More info ↗</a>`
      : "";

    return `<div class="popup-inner">
      <div class="popup-title">${p.name || "Parking Location"}</div>
      <div>
        <span class="popup-badge" style="background:${typeColor(p.type)}">${typeLabel(p.type)}</span>
        ${p.parking_class === "premium" || p.parking_class === "valet"
          ? `<span class="popup-badge" style="background:#6d28d9;margin-left:4px">Premium</span>` : ""}
      </div>
      ${row("Rate",          rateDisplay)}
      ${row("1st Hour",      p.first_hour_rate ? rm(p.first_hour_rate) + "/hr" : (firstHrFree ? "Free" : ""))}
      ${row("Daily Max",     rm(p.daily_max_cap))}
      ${row("Motorcycle",    p.motorcycle_rate ? rm(p.motorcycle_rate) + "/hr" : "")}
      ${row("Hours",         p.operating_hours)}
      ${row("Payment",       p.payment_method)}
      ${row("Operator",      p.operator)}
      ${row("Bays",          p.total_bays)}
      ${row("City",          p.city)}
      ${badges ? `<div style="margin-top:7px;font-size:12px;display:flex;gap:6px;flex-wrap:wrap;color:#555">${badges}</div>` : ""}
      ${p.notes ? `<div style="margin-top:6px;font-size:11px;color:var(--muted);font-style:italic">${p.notes}</div>` : ""}
      <div class="popup-footer">${sourceLink}</div>
    </div>`;
  }

  return { build, typeColor };
})();
