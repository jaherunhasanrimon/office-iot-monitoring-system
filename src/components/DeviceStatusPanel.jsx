// Placeholder — DeviceStatusPanel component
// Groups all 15 devices by room and renders status cards.
// Fans show a spinning animation when ON; Lights show amber glow when ON.

export default function DeviceStatusPanel({ devices }) {
  const rooms = {};
  devices.forEach((d) => {
    if (!rooms[d.room_name]) rooms[d.room_name] = [];
    rooms[d.room_name].push(d);
  });

  return (
    <section>
      <h2>Device Status</h2>
      {Object.entries(rooms).map(([roomName, roomDevices]) => (
        <div key={roomName}>
          <h3>{roomName}</h3>
          <div>
            {roomDevices.map((device) => (
              <div key={device.id} className={`device-card ${device.status ? "on" : "off"}`}>
                <span>{device.type === "fan" ? "🌀" : "💡"}</span>
                <span>{device.name}</span>
                <span>{device.status ? "ON" : "OFF"}</span>
                <span>{device.status ? `${device.power_watts}W` : "—"}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}
