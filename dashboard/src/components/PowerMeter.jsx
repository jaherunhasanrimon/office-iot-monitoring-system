/**
 * PowerMeter
 * Shows total office wattage, per-room breakdown with progress bars,
 * and today's estimated kWh.
 */

const MAX_WATTS = 750; // 15 devices × 50W avg theoretical max

export default function PowerMeter({ usage, todayKwh }) {
  const total   = usage?.total_watts ?? 0;
  const perRoom = usage?.per_room    ?? [];

  return (
    <section className="power-meter">
      {/* ── Total ── */}
      <div className="power-total">
        <div className="power-total-label">Office Total</div>
        <div className="power-total-value">
          {total}
          <span className="power-total-unit">W</span>
        </div>
        <div className="power-kwh">
          Today: <span>{Number(todayKwh).toFixed(3)} kWh</span>
        </div>
      </div>

      {/* ── Per-room ── */}
      <div>
        <div className="section-header" style={{ marginBottom: "0.75rem" }}>
          <span className="section-icon">⚡</span>
          <span className="section-title">Per-room consumption</span>
        </div>
        <div className="power-rooms">
          {perRoom.length > 0
            ? perRoom.map((r) => (
                <RoomMeter key={r.room_id} room={r} total={total} />
              ))
            : ["Drawing Room", "Work Room 1", "Work Room 2"].map((name) => (
                <RoomMeter key={name} room={{ room_name: name, watts: 0 }} total={0} />
              ))}
        </div>
      </div>
    </section>
  );
}

function RoomMeter({ room, total }) {
  const pct = total > 0 ? Math.min((room.watts / MAX_WATTS) * 100, 100) : 0;

  return (
    <div className="power-room-card">
      <div className="power-room-name">{room.room_name}</div>
      <div>
        <span className="power-room-value">{room.watts ?? 0}</span>
        <span className="power-room-unit">W</span>
      </div>
      <div className="power-room-bar">
        <div className="power-room-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
