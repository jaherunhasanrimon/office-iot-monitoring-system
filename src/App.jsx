import { useEffect, useState } from "react";
import { useLiveData } from "./hooks/useLiveData";
import DeviceStatusPanel from "./components/DeviceStatusPanel";
import PowerMeter from "./components/PowerMeter";
import AlertsPanel from "./components/AlertsPanel";
import "./index.css";

function Clock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <span className="header-time">
      {time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
    </span>
  );
}

export default function App() {
  const { devices, usage, todayKwh, alerts, connected, loading } = useLiveData();

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-left">
          <span className="header-logo">🏢</span>
          <div>
            <div className="header-title">Office IoT Monitor</div>
            <div className="header-subtitle">Lights · Fans · Discord</div>
          </div>
        </div>
        <div className="header-right">
          <Clock />
          <div className={`connection-badge ${connected ? "online" : "offline"}`}>
            <span className="dot" />
            {connected ? "Live" : "Disconnected"}
          </div>
        </div>
      </header>

      {/* ── Main grid ── */}
      <main className="main">
        {/* Power meter — full width top row */}
        <PowerMeter usage={usage} todayKwh={todayKwh} />

        {/* Device status panel — left column */}
        {loading
          ? <SkeletonPanel />
          : <DeviceStatusPanel devices={devices} />
        }

        {/* Sidebar — right column */}
        <div className="sidebar">
          <AlertsPanel alerts={alerts} />
        </div>
      </main>
    </div>
  );
}

function SkeletonPanel() {
  return (
    <section className="device-panel">
      <div className="section-header">
        <span className="section-icon">🏠</span>
        <span className="section-title">Device Status</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {[1, 2, 3].map((i) => (
          <div key={i}>
            <div className="skeleton" style={{ height: "16px", width: "120px", marginBottom: "0.75rem" }} />
            <div className="devices-grid">
              {[1, 2, 3, 4, 5].map((j) => (
                <div key={j} className="skeleton" style={{ height: "100px" }} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
