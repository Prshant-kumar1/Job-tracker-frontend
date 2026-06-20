import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApplications } from "../api";
import ApplicationCard from "../components/ApplicationCard";

const STATUS_OPTIONS = ["", "applied", "oa", "interview", "rejected", "offer"];

export default function ApplicationsList() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchApplications = (statusFilter) => {
    setLoading(true);
    setError("");
    getApplications(statusFilter)
      .then((res) => setApplications(res.data))
      .catch((err) => {
        if (err.response?.status === 401) {
          localStorage.removeItem("token");
          navigate("/login");
        } else {
          setError("Failed to load applications.");
        }
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchApplications(status);
  }, [status]);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Applications</h1>
        <button className="btn btn-primary" onClick={() => navigate("/applications/new")}>
          + New Application
        </button>
      </div>

      <div className="filter-bar">
        <label htmlFor="status-filter">Filter by status:</label>
        <select
          id="status-filter"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="filter-select"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s === "" ? "All" : s.charAt(0).toUpperCase() + s.slice(1)}
            </option>
          ))}
        </select>
        <span className="result-count">
          {applications.length} application{applications.length !== 1 ? "s" : ""}
        </span>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="page-loading">Loading applications…</div>
      ) : applications.length === 0 ? (
        <div className="empty-state-box">
          <p>No applications found.</p>
          <button className="btn btn-primary" onClick={() => navigate("/applications/new")}>
            Add your first application
          </button>
        </div>
      ) : (
        <div className="cards-grid">
          {applications.map((app) => (
            <ApplicationCard key={app.id} application={app} />
          ))}
        </div>
      )}
    </div>
  );
}
