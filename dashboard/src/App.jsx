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

  const activeDevices = devices.filter((d) => d.status).length;
  const activeAlerts = alerts.filter((a) => !a.resolved_at).length;

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-left">
          <div>
            <div className="header-title">office iot</div>
            <div className="header-subtitle">lights · fans · discord</div>
          </div>
        </div>
        <div className="header-right">
          <Clock />
          <div className={`connection-badge ${connected ? "online" : "offline"}`}>
            <span className="dot" />
            {connected ? "live" : "offline"}
          </div>
        </div>
      </header>

      {/* ── Hero Banner Section (Carbonex Style) ── */}
      <section className="hero-section">
        <div className="hero-left">
          <span className="hero-badge">we are</span>
          <h1 className="hero-title">solving global energy problems.</h1>
          <p className="hero-desc">
            carbonex tracks environmental solutions by monitoring and optimizing workspace energy footprints. our real-time smart engine cuts office waste and guarantees sustainable resource consumption.
          </p>
          <button className="hero-btn" onClick={() => window.scrollTo({ top: 750, behavior: "smooth" })}>
            view real-time data
          </button>
          
          <div className="hero-stats">
            <div className="hero-stat-card">
              <div className="hero-stat-val">{Number(todayKwh).toFixed(3)}</div>
              <div className="hero-stat-label">today's kwh estimated</div>
            </div>
            <div className="hero-stat-card">
              <div className="hero-stat-val">{activeDevices}</div>
              <div className="hero-stat-label">active office devices</div>
            </div>
            <div className="hero-stat-card">
              <div className="hero-stat-val">{activeAlerts}</div>
              <div className="hero-stat-label">active system alerts</div>
            </div>
          </div>
        </div>
        <div className="hero-right">
          <img 
            src="/hero-illustration.png" 
            alt="Eco-friendly Smart Office" 
            className="hero-img" 
          />
        </div>
      </section>

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

        {/* ── Footer ── */}
        <footer className="footer-editorial">
          <div className="footer-editorial-left">
            <span>purity of architecture</span>
            <span>•</span>
            <span>power of gemini</span>
            <span>•</span>
            <span>preservation of energy</span>
          </div>
          <div className="footer-editorial-right">
            <span>scroll down</span>
          </div>
        </footer>
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
