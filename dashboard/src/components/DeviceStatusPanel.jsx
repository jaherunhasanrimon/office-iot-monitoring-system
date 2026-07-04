/**
 * DeviceStatusPanel
 * Groups 15 devices by room, renders a card for each.
 * Fans animate (spin) when ON. Lights glow (amber pulse) when ON.
 */

export default function DeviceStatusPanel({ devices }) {
  // Group by room_name preserving order
  const roomOrder = ["Drawing Room", "Work Room 1", "Work Room 2"];
  const grouped   = {};
  roomOrder.forEach((r) => { grouped[r] = []; });
  devices.forEach((d) => {
    if (grouped[d.room_name]) grouped[d.room_name].push(d);
    else grouped[d.room_name] = [d];
  });

  const totalOn  = devices.filter((d) => d.status).length;
  const totalOff = devices.length - totalOn;

  return (
    <section className="device-panel">
      <div className="section-header">
        <span className="section-icon">🏠</span>
        <span className="section-title">Device Status</span>
        <span className="section-count">
          {totalOn} ON · {totalOff} OFF · {devices.length} total
        </span>
      </div>

      {roomOrder.map((roomName) => {
        const roomDevices = grouped[roomName] || [];
        if (!roomDevices.length) return null;
        const roomOn = roomDevices.filter((d) => d.status).length;
        return (
          <div className="room-group" key={roomName}>
            <div className="room-label">
              <span className="room-label-dot" />
              {roomName}
              <span style={{ marginLeft: "auto", fontSize: "0.72rem", color: "var(--text-muted)", fontFamily: "'JetBrains Mono', monospace" }}>
                {roomOn}/{roomDevices.length} active
              </span>
            </div>
            <div className="devices-grid">
              {roomDevices.map((device) => (
                <DeviceCard key={device.id} device={device} />
              ))}
            </div>
          </div>
        );
      })}
    </section>
  );
}

function DeviceCard({ device }) {
  const isOn = device.status;
  const isFan = device.type === "fan";

  return (
    <div className={`device-card ${isOn ? "on" : "off"}`}>
      <div className="device-card-top">
        <div className="device-icon-wrap">
          {isFan
            ? <span className={isOn ? "fan-icon" : ""} role="img" aria-label="fan">🌀</span>
            : <span className={isOn ? "light-icon" : ""} role="img" aria-label="light">💡</span>
          }
        </div>
        <span className="device-status-dot" title={isOn ? "ON" : "OFF"} />
      </div>

      <div className="device-name">{device.name}</div>

      <div className="device-footer">
        <span className="device-state">{isOn ? "ON" : "OFF"}</span>
        <span className="device-watts">
          {isOn ? `${device.power_watts}W` : "—"}
        </span>
      </div>
    </div>
  );
}
