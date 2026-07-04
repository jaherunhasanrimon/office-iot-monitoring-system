// Placeholder — PowerMeter component
// Shows total office wattage and per-room breakdown.

export default function PowerMeter({ usage, todayKwh }) {
  return (
    <section>
      <h2>Power Consumption</h2>
      <p>Total: <strong>{usage.total_watts}W</strong></p>
      <p>Today's estimate: <strong>{todayKwh.toFixed(2)} kWh</strong></p>
      <div>
        {(usage.per_room || []).map((r) => (
          <div key={r.room_id}>
            {r.room_name}: {r.watts}W
          </div>
        ))}
      </div>
    </section>
  );
}
