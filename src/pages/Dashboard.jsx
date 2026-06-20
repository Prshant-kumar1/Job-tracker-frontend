import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboardSummary } from "../api";
import StatusBadge from "../components/StatusBadge";

export default function Dashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboardSummary()
      .then((res) => setSummary(res.data))
      .catch((err) => {
        if (err.response?.status === 401) {
          localStorage.removeItem("token");
          navigate("/login");
        } else {
          setError("Failed to load dashboard.");
        }
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) return <div className="page-loading">Loading dashboard…</div>;
  if (error) return <div className="alert alert-error">{error}</div>;
  if (!summary) return null;

  const stats = [
    { label: "Total", value: summary.total_applications, cls: "stat-total" },
    { label: "Applied", value: summary.applied_count, cls: "stat-applied" },
    { label: "OA", value: summary.oa_count, cls: "stat-oa" },
    { label: "Interview", value: summary.interview_count, cls: "stat-interview" },
    { label: "Rejected", value: summary.rejected_count, cls: "stat-rejected" },
    { label: "Offer", value: summary.offer_count, cls: "stat-offer" },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <button className="btn btn-primary" onClick={() => navigate("/applications/new")}>
          + New Application
        </button>
      </div>

      <div className="stats-grid">
        {stats.map((s) => (
          <div key={s.label} className={`stat-card ${s.cls}`}>
            <span className="stat-value">{s.value}</span>
            <span className="stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      <div className="dashboard-sections">
        <section className="dashboard-section">
          <h2>Recent Applications</h2>
          {summary.recent_applications && summary.recent_applications.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Applied</th>
                </tr>
              </thead>
              <tbody>
                {summary.recent_applications.map((app) => (
                  <tr
                    key={app.id}
                    className="table-row-clickable"
                    onClick={() => navigate(`/applications/${app.id}`)}
                  >
                    <td>{app.company}</td>
                    <td>{app.role}</td>
                    <td><StatusBadge status={app.status} /></td>
                    <td>
                      {app.date_applied
                        ? new Date(app.date_applied).toLocaleDateString()
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty-state">No recent applications.</p>
          )}
        </section>

        <section className="dashboard-section">
          <h2>Upcoming Follow-ups</h2>
          {summary.upcoming_followups && summary.upcoming_followups.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Role</th>
                  <th>Follow-up Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {summary.upcoming_followups.map((app) => (
                  <tr
                    key={app.id}
                    className="table-row-clickable"
                    onClick={() => navigate(`/applications/${app.id}`)}
                  >
                    <td>{app.company}</td>
                    <td>{app.role}</td>
                    <td>
                      {app.follow_up_date
                        ? new Date(app.follow_up_date).toLocaleDateString()
                        : "—"}
                    </td>
                    <td><StatusBadge status={app.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty-state">No upcoming follow-ups.</p>
          )}
        </section>
      </div>
    </div>
  );
}
