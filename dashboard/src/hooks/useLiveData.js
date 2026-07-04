import { useEffect, useState, useRef, useCallback } from "react";
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

  // ── Initial data fetch ────────────────────────────────────────────────────
  // useCallback gives fetchAll a stable reference so it can safely be called
  // from both the initial effect and the reconnect handler without stale closures.
  const fetchAll = useCallback(async () => {
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
  }, []); // no deps — reads from API_URL constant only

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // ── WebSocket subscription ────────────────────────────────────────────────
  useEffect(() => {
    // FIX: Connect using a relative origin ("/") so the request goes through
    // the Vite dev-server proxy (configured in vite.config.js with ws:true).
    // The old direct URL "http://localhost:5000" bypassed the proxy, causing
    // the WebSocket upgrade to silently fail and leaving the dashboard stale.
    //
    // In production (no Vite proxy), set VITE_SOCKET_URL in the env and
    // connect directly to the backend host.
    const socketUrl = import.meta.env.VITE_SOCKET_URL || "/";

    const socket = io(socketUrl, {
      path: "/socket.io",
      // Start with polling so the handshake is reliable, then upgrade to WS.
      // Putting "websocket" first caused a race where the WS attempt failed
      // silently before polling could establish the session.
      transports: ["polling", "websocket"],
      reconnectionDelay: 1000,
      reconnectionAttempts: Infinity,
    });
    socketRef.current = socket;

    socket.on("connect", () => {
      setConnected(true);
      fetchAll(); // re-sync on (re)connect to catch any missed ticks
    });

    socket.on("disconnect", () => setConnected(false));

    socket.on("connect_error", (err) => {
      console.error("[useLiveData] Socket.IO connection error:", err.message);
    });

    // ── Device & power events (pushed by simulator tick) ─────────────────
    socket.on("device_update", (updated) => {
      setDevices((prev) =>
        prev.map((d) => (d.id === updated.id ? { ...d, ...updated } : d))
      );
    });

    socket.on("usage_update", (data) => {
      setUsage({
        total_watts: data.total_watts,
        per_room: data.per_room,
      });
      setTodayKwh(data.estimated_kwh ?? 0);
    });

    // ── Alert events ──────────────────────────────────────────────────────
    socket.on("alert_created", (newAlert) => {
      setAlerts((prev) => {
        // Avoid duplicates if fetchAll and the push arrive close together
        if (prev.some((a) => a.id === newAlert.id)) return prev;
        return [newAlert, ...prev];
      });
    });

    // FIX: Handle alert resolutions so the dashboard removes cleared alerts
    // in real-time. Previously, resolved alerts stayed visible forever because
    // the backend only set resolved_at in the DB without emitting any event.
    socket.on("alert_resolved", ({ id }) => {
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    });

    // ── 5-second fallback poll ────────────────────────────────────────────
    // Belt-and-suspenders: re-sync full state every 5 s even if a Socket.IO
    // event is missed (e.g. during a reconnect gap). Keeps the dashboard
    // accurate without hammering the backend.
    const pollId = setInterval(fetchAll, 5_000);

    return () => {
      socket.disconnect();
      clearInterval(pollId);
    };
  }, [fetchAll]);

  return { devices, usage, todayKwh, alerts, connected, loading };
}
