import { useLiveData } from "./hooks/useLiveData";
import DeviceStatusPanel from "./components/DeviceStatusPanel";
import PowerMeter from "./components/PowerMeter";
import AlertsPanel from "./components/AlertsPanel";

export default function App() {
  const { devices, usage, todayKwh, alerts, connected } = useLiveData();

  return (
    <div className="app">
      <header>
        <h1>🏢 Office IoT Monitor</h1>
        <span className={`connection-badge ${connected ? "online" : "offline"}`}>
          {connected ? "● Live" : "○ Disconnected"}
        </span>
      </header>

      <main>
        <DeviceStatusPanel devices={devices} />
        <PowerMeter usage={usage} todayKwh={todayKwh} />
        <AlertsPanel alerts={alerts} />
      </main>
    </div>
  );
}
