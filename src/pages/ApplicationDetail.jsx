import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  getApplication,
  updateApplication,
  deleteApplication,
  getAiSuggestion,
} from "../api";
import StatusBadge from "../components/StatusBadge";

const STATUS_OPTIONS = ["applied", "oa", "interview", "rejected", "offer"];

export default function ApplicationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    getApplication(id)
      .then((res) => {
        setApplication(res.data);
        setForm(toFormValues(res.data));
      })
      .catch((err) => {
        if (err.response?.status === 401) {
          localStorage.removeItem("token");
          navigate("/login");
        } else if (err.response?.status === 404) {
          navigate("/applications");
        } else {
          setError("Failed to load application.");
        }
      })
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const toFormValues = (app) => ({
    company: app.company || "",
    role: app.role || "",
    location: app.location || "",
    apply_link: app.apply_link || "",
    date_applied: app.date_applied ? app.date_applied.substring(0, 10) : "",
    status: app.status || "applied",
    resume_version: app.resume_version || "",
    notes: app.notes || "",
    follow_up_date: app.follow_up_date
      ? app.follow_up_date.substring(0, 10)
      : "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);

    const payload = { ...form };
    if (!payload.date_applied) delete payload.date_applied;
    if (!payload.follow_up_date) delete payload.follow_up_date;
    if (!payload.location) delete payload.location;
    if (!payload.apply_link) delete payload.apply_link;
    if (!payload.resume_version) delete payload.resume_version;
    if (!payload.notes) delete payload.notes;

    try {
      const res = await updateApplication(id, payload);
      setApplication(res.data);
      setForm(toFormValues(res.data));
      setEditing(false);
      setSuccess("Application updated successfully.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(", "));
      } else {
        setError(detail || "Failed to update application.");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Delete application at ${application.company}? This cannot be undone.`)) return;
    setDeleting(true);
    try {
      await deleteApplication(id);
      navigate("/applications");
    } catch {
      setError("Failed to delete application.");
      setDeleting(false);
    }
  };

  const handleAiSuggest = async () => {
    setAiLoading(true);
    setAiSuggestion("");
    setError("");
    try {
      const res = await getAiSuggestion(id);
      setAiSuggestion(res.data.suggestion);
    } catch (err) {
      setError(
        err.response?.data?.detail || "AI suggestion failed. Please try again."
      );
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) return <div className="page-loading">Loading application…</div>;
  if (!application && !error) return null;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate("/applications")}
          >
            ← Back
          </button>
          <h1>{application ? `${application.company} — ${application.role}` : "Application"}</h1>
        </div>
        <div className="page-header-actions">
          {!editing && (
            <button className="btn btn-secondary" onClick={() => { setEditing(true); setSuccess(""); setError(""); }}>
              Edit
            </button>
          )}
          <button
            className="btn btn-danger"
            onClick={handleDelete}
            disabled={deleting}
          >
            {deleting ? "Deleting…" : "Delete"}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {!editing ? (
        <div className="detail-view">
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Company</span>
              <span className="detail-value">{application.company}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Role</span>
              <span className="detail-value">{application.role}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Status</span>
              <span className="detail-value">
                <StatusBadge status={application.status} />
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Location</span>
              <span className="detail-value">{application.location || "—"}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Date Applied</span>
              <span className="detail-value">
                {application.date_applied
                  ? new Date(application.date_applied).toLocaleDateString()
                  : "—"}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Follow-up Date</span>
              <span className="detail-value">
                {application.follow_up_date
                  ? new Date(application.follow_up_date).toLocaleDateString()
                  : "—"}
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Resume Version</span>
              <span className="detail-value">{application.resume_version || "—"}</span>
            </div>
            {application.apply_link && (
              <div className="detail-item">
                <span className="detail-label">Application Link</span>
                <span className="detail-value">
                  <a href={application.apply_link} target="_blank" rel="noreferrer" className="link">
                    View Posting
                  </a>
                </span>
              </div>
            )}
          </div>

          {application.notes && (
            <div className="detail-notes">
              <span className="detail-label">Notes</span>
              <p className="notes-text">{application.notes}</p>
            </div>
          )}

          <div className="ai-section">
            <div className="ai-header">
              <h2>AI Suggestion</h2>
              <button
                className="btn btn-ai"
                onClick={handleAiSuggest}
                disabled={aiLoading}
              >
                {aiLoading ? "Thinking…" : "✨ Get AI Suggestion"}
              </button>
            </div>
            {aiSuggestion && (
              <div className="ai-suggestion-box">
                <p>{aiSuggestion}</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <form onSubmit={handleSave} className="app-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="company">Company *</label>
              <input
                id="company"
                type="text"
                name="company"
                value={form.company}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="role">Role *</label>
              <input
                id="role"
                type="text"
                name="role"
                value={form.role}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input
                id="location"
                type="text"
                name="location"
                value={form.location}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="status">Status *</label>
              <select
                id="status"
                name="status"
                value={form.status}
                onChange={handleChange}
                required
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="date_applied">Date Applied</label>
              <input
                id="date_applied"
                type="date"
                name="date_applied"
                value={form.date_applied}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="follow_up_date">Follow-up Date</label>
              <input
                id="follow_up_date"
                type="date"
                name="follow_up_date"
                value={form.follow_up_date}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="apply_link">Application Link</label>
              <input
                id="apply_link"
                type="url"
                name="apply_link"
                value={form.apply_link}
                onChange={handleChange}
                placeholder="https://..."
              />
            </div>
            <div className="form-group">
              <label htmlFor="resume_version">Resume Version</label>
              <input
                id="resume_version"
                type="text"
                name="resume_version"
                value={form.resume_version}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="notes">Notes</label>
            <textarea
              id="notes"
              name="notes"
              value={form.notes}
              onChange={handleChange}
              rows={4}
            />
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Save Changes"}
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => { setEditing(false); setForm(toFormValues(application)); setError(""); }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
