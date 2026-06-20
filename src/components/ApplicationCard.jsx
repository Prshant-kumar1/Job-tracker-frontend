import { useNavigate } from "react-router-dom";
import StatusBadge from "./StatusBadge";

export default function ApplicationCard({ application }) {
  const navigate = useNavigate();

  return (
    <div
      className="app-card"
      onClick={() => navigate(`/applications/${application.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter") navigate(`/applications/${application.id}`);
      }}
    >
      <div className="app-card-header">
        <div>
          <h3 className="app-card-company">{application.company}</h3>
          <p className="app-card-role">{application.role}</p>
        </div>
        <StatusBadge status={application.status} />
      </div>
      <div className="app-card-meta">
        {application.location && (
          <span className="meta-item">&#128205; {application.location}</span>
        )}
        {application.date_applied && (
          <span className="meta-item">
            &#128197; {new Date(application.date_applied).toLocaleDateString()}
          </span>
        )}
        {application.follow_up_date && (
          <span className="meta-item">
            &#9201; Follow-up:{" "}
            {new Date(application.follow_up_date).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
}
