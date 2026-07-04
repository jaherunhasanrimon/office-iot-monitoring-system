// Placeholder — AlertsPanel component
// Shows active alerts, newest first, with timestamp and type badge.

export default function AlertsPanel({ alerts }) {
  const active = alerts.filter((a) => a.is_active);

  return (
    <section>
      <h2>Active Alerts {active.length > 0 && <span>({active.length})</span>}</h2>
      {active.length === 0 ? (
        <p>No active alerts ✅</p>
      ) : (
        active.map((alert) => (
          <div key={alert.id} className={`alert-card ${alert.type}`}>
            <span className="badge">{alert.type === "after_hours" ? "After Hours" : "Prolonged ON"}</span>
            <p>{alert.message}</p>
            <small>{new Date(alert.created_at).toLocaleString()}</small>
          </div>
        ))
      )}
    </section>
  );
}
