/**
 * api.js — Fetch parking data from the FastAPI backend.
 * Exposes: ParkingAPI.getAll(), ParkingAPI.getStats(), ParkingAPI.getZones()
 */

const ParkingAPI = (() => {
  const BASE = "/api";

  async function getAll(params = {}) {
    const qs = new URLSearchParams(params).toString();
    const url = qs ? `${BASE}/parking?${qs}` : `${BASE}/parking`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
    return res.json(); // GeoJSON FeatureCollection
  }

  async function getById(id) {
    const res = await fetch(`${BASE}/parking/${id}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  }

  async function getStats() {
    const res = await fetch(`${BASE}/stats`);
    if (!res.ok) throw new Error(`Stats API error ${res.status}`);
    return res.json();
  }

  async function getZones(city) {
    const url = city ? `${BASE}/zones?city=${encodeURIComponent(city)}` : `${BASE}/zones`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Zones API error ${res.status}`);
    return res.json();
  }

  return { getAll, getById, getStats, getZones };
})();
