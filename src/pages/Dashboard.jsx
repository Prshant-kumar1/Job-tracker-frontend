import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboardSummary, getApplications } from "../api";
import StatusBadge from "../components/StatusBadge";
import AnimatedNumber from "../components/AnimatedNumber";
import DonutChart from "../components/charts/DonutChart";
import TrendLineChart from "../components/charts/TrendLineChart";

const STATUS_COLORS = {
  applied: "#8b7bff",
  oa: "#36e2c4",
  interview: "#ffb84d",
  rejected: "#ff6b8a",
  offer: "#3ee08e",
};

// Cycle of chip colors used for company initials in tables — purely
// presentational, picked deterministically from the company name so the
// same company always gets the same color.
const CHIP_PALETTE = [
  { bg: "rgba(139,123,255,.18)", color: "#b7adff" },
  { bg: "rgba(54,226,196,.18)", color: "#7eecd9" },
  { bg: "rgba(255,184,77,.18)", color: "#ffcb80" },
  { bg: "rgba(255,107,138,.18)", color: "#ff9bb0" },
  { bg: "rgba(62,224,142,.18)", color: "#80edae" },
];

function chipStyleFor(name) {
  if (!name) return CHIP_PALETTE[0];
  const code = name.charCodeAt(0) + name.length;
  return CHIP_PALETTE[code % CHIP_PALETTE.length];
}

// The backend serializes date_applied/follow_up_date as plain "YYYY-MM-DD"
// (Python `date`, not `datetime`). new Date("YYYY-MM-DD") parses that as
// UTC midnight, which rolls back a day once converted to local time for
// any UTC-negative timezone. Parsing the components manually keeps the
// date anchored to the calendar day the backend actually meant.
function parseDateOnly(dateStr) {
  if (!dateStr) return null;
  const [year, month, day] = dateStr.split("-").map(Number);
  if (!year || !month || !day) return null;
  return new Date(year, month - 1, day);
}

function formatFollowup(dateStr) {
  const target = parseDateOnly(dateStr);
  if (!target) return "—";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const days = Math.round((target - today) / (1000 * 60 * 60 * 24));
  if (days < 0) return "Overdue";
  if (days === 0) return "Today";
  if (days === 1) return "Tomorrow";
  return `In ${days} days`;
}

// Buckets every application's date_applied into the last 8 weeks, relative
// to today. Entirely derived from real data already returned by
// GET /applications — no backend changes needed.
function buildWeeklyTrend(applications) {
  const weeks = 8;
  const counts = new Array(weeks).fill(0);
  const now = new Date();
  const msPerWeek = 7 * 24 * 60 * 60 * 1000;

  applications.forEach((app) => {
    const applied = parseDateOnly(app.date_applied);
    if (!applied) return;
    const diffMs = now - applied;
    if (diffMs < 0) return;
    const weekIndex = weeks - 1 - Math.floor(diffMs / msPerWeek);
    if (weekIndex >= 0 && weekIndex < weeks) {
      counts[weekIndex] += 1;
    }
  });

  const labels = Array.from({ length: weeks }, (_, i) => `Wk ${i + 1}`);
  return { labels, counts };
}

const STAT_ICONS = {
  total: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
    </svg>
  ),
  applied: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
    </svg>
  ),
  oa: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M9 11l3 3L22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </svg>
  ),
  interview: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  ),
  rejected: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M18 6L6 18M6 6l12 12" />
    </svg>
  ),
  offer: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M20 7h-9a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z" />
      <path d="M16 3v4M8 3v4M4 11h16" />
    </svg>
  ),
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState({ labels: [], counts: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getDashboardSummary(), getApplications()])
      .then(([summaryRes, applicationsRes]) => {
        setSummary(summaryRes.data);
        setTrend(buildWeeklyTrend(applicationsRes.data || []));
      })
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
    { key: "total", label: "Total", value: summary.total_applications },
    { key: "applied", label: "Applied", value: summary.applied_count },
    { key: "oa", label: "OA", value: summary.oa_count },
    { key: "interview", label: "Interview", value: summary.interview_count },
    { key: "rejected", label: "Rejected", value: summary.rejected_count },
    { key: "offer", label: "Offer", value: summary.offer_count },
  ];

  const donutData = [
    { label: "Applied", value: summary.applied_count },
    { label: "OA", value: summary.oa_count },
    { label: "Interview", value: summary.interview_count },
    { label: "Rejected", value: summary.rejected_count },
    { label: "Offer", value: summary.offer_count },
  ];
  const donutColors = donutData.map((d) => STATUS_COLORS[d.label.toLowerCase()] || STATUS_COLORS.applied);
  const hasAnyApplications = summary.total_applications > 0;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <button className="btn btn-primary" onClick={() => navigate("/applications/new")}>
          + New Application
        </button>
      </div>

      <div className="stats-grid">
        {stats.map((s, i) => (
          <div
            key={s.key}
            className={`stat-card fade-up stat-${s.key}`}
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            <div className={`stat-icon ${s.key}`}>{STAT_ICONS[s.key]}</div>
            <span className="stat-value">
              <AnimatedNumber value={s.value} />
            </span>
            <span className="stat-label">{s.label}</span>
          </div>
        ))}
      </div>

      {hasAnyApplications && (
        <div className="charts-row">
          <div className="chart-panel fade-up" style={{ animationDelay: "0.3s" }}>
            <div className="panel-header">
              <div>
                <h2>Status breakdown</h2>
                <div className="sub">Across all {summary.total_applications} applications</div>
              </div>
            </div>
            <div className="donut-wrap">
              <DonutChart data={donutData} colors={donutColors} total={summary.total_applications} />
              <div className="legend-list">
                {donutData.map((d, i) => (
                  <div className="legend-row" key={d.label}>
                    <div className="legend-left">
                      <span className="dot" style={{ background: donutColors[i] }}></span>
                      {d.label}
                    </div>
                    <span className="legend-val">{d.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="chart-panel fade-up" style={{ animationDelay: "0.35s" }}>
            <div className="panel-header">
              <div>
                <h2>Applications over time</h2>
                <div className="sub">Last 8 weeks</div>
              </div>
            </div>
            <TrendLineChart labels={trend.labels} data={trend.counts} />
          </div>
        </div>
      )}

      <div className="dashboard-sections">
        <section className="dashboard-section fade-up" style={{ animationDelay: "0.4s" }}>
          <h2>Recent Applications</h2>
          {summary.recent_applications && summary.recent_applications.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Applied</th>
                </tr>
              </thead>
              <tbody>
                {summary.recent_applications.map((app) => {
                  const chip = chipStyleFor(app.company);
                  return (
                    <tr
                      key={app.id}
                      className="table-row-clickable"
                      onClick={() => navigate(`/applications/${app.id}`)}
                    >
                      <td>
                        <div className="company-cell">
                          <div className="logo-chip" style={{ background: chip.bg, color: chip.color }}>
                            {app.company?.charAt(0).toUpperCase() || "?"}
                          </div>
                          <div>
                            <div className="co-name">{app.company}</div>
                            <div className="co-role">{app.role}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={app.status} />
                      </td>
                      <td className="date-cell">
                        {app.date_applied ? new Date(app.date_applied).toLocaleDateString() : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <p className="empty-state-inline">No applications yet — once you log one, it'll show up here.</p>
          )}
        </section>

        <section className="dashboard-section fade-up" style={{ animationDelay: "0.45s" }}>
          <h2>Upcoming Follow-ups</h2>
          {summary.upcoming_followups && summary.upcoming_followups.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Role</th>
                  <th>Follow-up</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {summary.upcoming_followups.map((app) => {
                  const chip = chipStyleFor(app.company);
                  return (
                    <tr
                      key={app.id}
                      className="table-row-clickable"
                      onClick={() => navigate(`/applications/${app.id}`)}
                    >
                      <td>
                        <div className="company-cell">
                          <div className="logo-chip" style={{ background: chip.bg, color: chip.color }}>
                            {app.company?.charAt(0).toUpperCase() || "?"}
                          </div>
                          <div className="co-name">{app.company}</div>
                        </div>
                      </td>
                      <td className="date-cell">{app.role}</td>
                      <td>
                        <span className="countdown-badge">{formatFollowup(app.follow_up_date)}</span>
                      </td>
                      <td>
                        <StatusBadge status={app.status} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
                  <path d="M12 2l2.5 6.5L21 9l-5 4.5L17.5 21 12 17l-5.5 4L8 13.5 3 9l6.5-.5z" />
                </svg>
              </div>
              <h3>Nothing to follow up on</h3>
              <p>Set a follow-up date on an application and it'll show up here as a reminder.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
