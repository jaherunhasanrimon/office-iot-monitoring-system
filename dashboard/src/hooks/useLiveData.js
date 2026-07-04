import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export function useLiveData() {
  const [devices, setDevices] = useState([]);
  const [usage, setUsage] = useState({ total_watts: 0, per_room: [] });
  const [todayKwh, setTodayKwh] = useState(0);
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);

  // Initial data fetch
  useEffect(() => {
    async function fetchAll() {
      try {
        const [devRes, usageRes, todayRes, alertRes] = await Promise.all([
          fetch(`${API_URL}/api/devices`),
          fetch(`${API_URL}/api/usage/current`),
          fetch(`${API_URL}/api/usage/today`),
          fetch(`${API_URL}/api/alerts`),
        ]);
        setDevices(await devRes.json());
        setUsage(await usageRes.json());
        setTodayKwh((await todayRes.json()).estimated_kwh);
        setAlerts(await alertRes.json());
      } catch (err) {
        console.error("[useLiveData] Initial fetch failed:", err);
      }
    }
    fetchAll();
  }, []);

  // WebSocket subscription for live updates
  useEffect(() => {
    const socket = io(API_URL, { transports: ["websocket", "polling"] });

    socket.on("connect", () => {
      console.log("[Socket] Connected:", socket.id);
      setConnected(true);
    });

    socket.on("disconnect", () => {
      console.warn("[Socket] Disconnected");
      setConnected(false);
    });

    socket.on("device_update", (updatedDevice) => {
      setDevices((prev) =>
        prev.map((d) => (d.id === updatedDevice.id ? updatedDevice : d))
      );
      // Refresh usage totals after a device change
      fetch(`${API_URL}/api/usage/current`)
        .then((r) => r.json())
        .then(setUsage)
        .catch(console.error);
    });

    socket.on("alert_created", (newAlert) => {
      setAlerts((prev) => [newAlert, ...prev]);
    });

    return () => socket.disconnect();
  }, []);

  return { devices, usage, todayKwh, alerts, connected };
}
