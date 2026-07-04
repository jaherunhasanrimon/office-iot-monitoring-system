import { useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export function useLiveData() {
  const [devices, setDevices]     = useState([]);
  const [usage, setUsage]         = useState({ total_watts: 0, per_room: [] });
  const [todayKwh, setTodayKwh]   = useState(0);
  const [alerts, setAlerts]       = useState([]);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading]     = useState(true);
  const socketRef                 = useRef(null);

  // ── Initial data fetch ────────────────────────────────────
  async function fetchAll() {
    try {
      const [devRes, usageRes, todayRes, alertRes] = await Promise.all([
        fetch(`${API_URL}/api/devices`),
        fetch(`${API_URL}/api/usage/current`),
        fetch(`${API_URL}/api/usage/today`),
        fetch(`${API_URL}/api/alerts`),
      ]);
      if (devRes.ok)   setDevices(await devRes.json());
      if (usageRes.ok) setUsage(await usageRes.json());
      if (todayRes.ok) setTodayKwh((await todayRes.json()).estimated_kwh ?? 0);
      if (alertRes.ok) setAlerts(await alertRes.json());
    } catch (err) {
      console.error("[useLiveData] Initial fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchAll(); }, []);

  // ── WebSocket subscription ─────────────────────────────────
  useEffect(() => {
    const socket = io(API_URL, {
      transports: ["websocket", "polling"],
      reconnectionDelay: 1000,
      reconnectionAttempts: 20,
    });
    socketRef.current = socket;

    socket.on("connect", () => {
      setConnected(true);
      fetchAll(); // re-sync on reconnect
    });

    socket.on("disconnect", () => setConnected(false));

    socket.on("device_update", (updated) => {
      setDevices((prev) =>
        prev.map((d) => (d.id === updated.id ? { ...d, ...updated } : d))
      );
      // Refresh usage totals
      fetch(`${API_URL}/api/usage/current`)
        .then((r) => r.ok ? r.json() : null)
        .then((data) => { if (data) setUsage(data); })
        .catch(() => {});
      fetch(`${API_URL}/api/usage/today`)
        .then((r) => r.ok ? r.json() : null)
        .then((data) => { if (data) setTodayKwh(data.estimated_kwh ?? 0); })
        .catch(() => {});
    });

    socket.on("alert_created", (newAlert) => {
      setAlerts((prev) => {
        // Avoid duplicates
        if (prev.some((a) => a.id === newAlert.id)) return prev;
        return [newAlert, ...prev];
      });
    });

    return () => socket.disconnect();
  }, []);

  return { devices, usage, todayKwh, alerts, connected, loading };
}
