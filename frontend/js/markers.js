/**
 * markers.js — Creates colour-coded Leaflet DivIcons and adds features to the cluster layer.
 * Exposes: ParkingMarkers.colorClass(props), ParkingMarkers.makeIcon(props),
 *          ParkingMarkers.addFeatures(geojson, clusterGroup, onEachFeature)
 */

const ParkingMarkers = (() => {

  /**
   * Returns a CSS class name based on the rate of the parking feature.
   * Colour scale:
   *   grey   → free / flat ≤ RM1
   *   green  → RM1–2/hr
   *   amber  → RM2–4/hr
   *   red    → RM4+/hr
   *   violet → valet / premium
   *   teal   → park & ride
   */
  function colorClass(p) {
    const t = (p.type || "").toLowerCase();
    if (t === "valet")         return "marker-valet";
    if (t === "park_and_ride") return "marker-pr";
    if (t === "airport") {
      const r = parseFloat(p.rate_per_hour);
      return isNaN(r) ? "marker-high" : (r >= 4 ? "marker-high" : "marker-mid");
    }
    const r = parseFloat(p.rate_per_hour);
    if (isNaN(r) || r <= 0)  return "marker-free";
    if (r <= 1)               return "marker-free";
    if (r <= 2)               return "marker-low";
    if (r <= 4)               return "marker-mid";
    return "marker-high";
  }

  /**
   * Label shown on the marker pin (compact rate string).
   */
  function pinLabel(p) {
    const t = (p.type || "").toLowerCase();
    if (t === "valet") {
      return p.valet_rate ? `RM${parseFloat(p.valet_rate).toFixed(0)}` : "Valet";
    }
    if (t === "park_and_ride") return "P&R";
    const r = parseFloat(p.rate_per_hour);
    if (isNaN(r) || r === 0) return "Free";
    return `RM${r % 1 === 0 ? r : r.toFixed(1)}`;
  }

  /**
   * Creates a DivIcon for the parking marker.
   */
  function makeIcon(p) {
    const cls  = colorClass(p);
    const label = pinLabel(p);
    return L.divIcon({
      className: "",   // prevent Leaflet's default white square
      html: `<div class="parking-marker ${cls}" style="width:38px;height:38px;">
               <span>${label}</span>
             </div>`,
      iconSize:   [38, 38],
      iconAnchor: [19, 38],
      popupAnchor:[0, -40],
    });
  }

  /**
   * Add all features from a GeoJSON FeatureCollection to a MarkerClusterGroup.
   * @param {object}   geojson       – GeoJSON FeatureCollection
   * @param {object}   clusterGroup  – L.MarkerClusterGroup instance
   * @param {Function} onEachFeature – callback(feature, marker)
   * @returns {L.Marker[]} array of created markers (each has feature stored as .feature)
   */
  function addFeatures(geojson, clusterGroup, onEachFeature) {
    const markers = [];
    (geojson.features || []).forEach(feature => {
      const coords = feature.geometry && feature.geometry.coordinates;
      if (!coords) return;
      const [lng, lat] = coords;
      if (!lat || !lng) return;

      const icon   = makeIcon(feature.properties);
      const marker = L.marker([lat, lng], { icon });
      marker.feature = feature;  // store for filtering

      marker.bindPopup(ParkingPopup.build(feature.properties), {
        maxWidth: 310,
        className: "parking-popup",
      });

      if (typeof onEachFeature === "function") {
        onEachFeature(feature, marker);
      }

      clusterGroup.addLayer(marker);
      markers.push(marker);
    });
    return markers;
  }

  return { colorClass, makeIcon, addFeatures };
})();
