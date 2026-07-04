/**
 * AlertsPanel
 * Shows active alerts, newest first.
 * Two alert types: after_hours (red) and prolonged_room_on (amber).
 */

function timeAgo(isoStr) {
  if (!isoStr) return "";
  const diff = Date.now() - new Date(isoStr + "Z").getTime(); // UTC
  const mins = Math.floor(diff / 60000);
  if (mins < 1)   return "just now";
  if (mins < 60)  return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)   return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

const TYPE_LABELS = {
  after_hours:       "After Hours",
  prolonged_room_on: "Prolonged ON",
};

const TYPE_ICONS = {
  after_hours:       "🌙",
  prolonged_room_on: "⏰",
};

export default function AlertsPanel({ alerts }) {
  const active = alerts.filter((a) => a.is_active !== false && !a.resolved_at);

  return (
    <section className="alerts-panel">
      <div className="section-header">
        <span className="section-icon">🚨</span>
        <span className="section-title">
          Active Alerts
          {active.length > 0 && (
            <span className="alerts-count-badge">{active.length}</span>
          )}
        </span>
      </div>

      {active.length === 0 ? (
        <div className="alerts-empty">
          <div className="alerts-empty-icon">✅</div>
          <div className="alerts-empty-text">No active alerts</div>
        </div>
      ) : (
        <div className="alerts-list">
          {active.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </section>
  );
}

function AlertCard({ alert }) {
  return (
    <div className={`alert-card ${alert.type}`}>
      <div className="alert-card-header">
        <span>{TYPE_ICONS[alert.type] ?? "⚠️"}</span>
        <span className={`alert-badge ${alert.type}`}>
          {TYPE_LABELS[alert.type] ?? alert.type}
        </span>
      </div>
      <div className="alert-message">{alert.message}</div>
      <div className="alert-time">{timeAgo(alert.created_at)}</div>
    </div>
  );
}
