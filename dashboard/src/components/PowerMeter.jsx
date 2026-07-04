/**
 * PowerMeter
 * Shows total office wattage and per-room inline cards with progress bars.
 */

const MAX_WATTS = 250; // 5 devices × 50W theoretical room max

export default function PowerMeter({ usage, todayKwh }) {
  const total   = usage?.total_watts ?? 0;
  const perRoom = usage?.per_room    ?? [];

  return (
    <section className="power-meter">
      {/* ── Title ── */}
      <div className="power-meter-header">
        <span className="power-meter-icon">⚡</span>
        <span className="power-meter-title">Power Meter</span>
      </div>

      <div className="power-meter-content">
        {/* ── Left Side: Total Watts ── */}
        <div className="power-total">
          <div className="power-total-value-row">
            <span className="power-total-value">{total}</span>
            <div className="power-total-unit-group">
              <span className="power-total-badge">Total</span>
              <span className="power-total-unit">W</span>
            </div>
          </div>
          <div className="power-kwh">
            Today: {Number(todayKwh).toFixed(3)} kWh
          </div>
        </div>

        {/* ── Right Side: Per-Room Breakdown Cards ── */}
        <div className="power-rooms">
          {perRoom.length > 0
            ? perRoom.map((r) => (
                <RoomMeter key={r.room_id} room={r} />
              ))
            : ["Drawing Room", "Work Room 1", "Work Room 2"].map((name) => (
                <RoomMeter key={name} room={{ room_name: name, watts: 0 }} />
              ))}
        </div>
      </div>
    </section>
  );
}

function RoomMeter({ room }) {
  const pct = Math.min((room.watts / MAX_WATTS) * 100, 100);

  return (
    <div className="power-room-card">
      <div className="power-room-header">
        <span className="power-room-name">{room.room_name}:</span>
        <span className="power-room-value">{room.watts ?? 0}W</span>
      </div>
      <div className="power-room-bar">
        <div className="power-room-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
