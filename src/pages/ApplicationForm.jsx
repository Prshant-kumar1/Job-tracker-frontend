import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createApplication } from "../api";

const STATUS_OPTIONS = ["applied", "oa", "interview", "rejected", "offer"];

const EMPTY_FORM = {
  company: "",
  role: "",
  location: "",
  apply_link: "",
  date_applied: "",
  status: "applied",
  resume_version: "",
  notes: "",
  follow_up_date: "",
};

export default function ApplicationForm() {
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const payload = { ...form };
    if (!payload.date_applied) delete payload.date_applied;
    if (!payload.follow_up_date) delete payload.follow_up_date;
    if (!payload.location) delete payload.location;
    if (!payload.apply_link) delete payload.apply_link;
    if (!payload.resume_version) delete payload.resume_version;
    if (!payload.notes) delete payload.notes;

    try {
      const res = await createApplication(payload);
      navigate(`/applications/${res.data.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(", "));
      } else {
        setError(detail || "Failed to create application.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>New Application</h1>
        <button className="btn btn-ghost" onClick={() => navigate("/applications")}>
          Cancel
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit} className="app-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="company">Company *</label>
            <input
              id="company"
              type="text"
              name="company"
              value={form.company}
              onChange={handleChange}
              placeholder="Acme Corp"
              required
              autoFocus
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
              placeholder="Software Engineer"
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
              placeholder="San Francisco, CA"
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
              placeholder="v2 - Senior"
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
            placeholder="Any notes about this application…"
            rows={4}
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Saving…" : "Save Application"}
          </button>
        </div>
      </form>
    </div>
  );
}
