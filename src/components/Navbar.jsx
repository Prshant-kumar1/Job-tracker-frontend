import { NavLink, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-icon">&#128188;</span>
        <span className="logo-text">JobTracker</span>
      </div>

      {token && (
        <ul className="sidebar-nav">
          <li>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <span className="nav-icon">&#9783;</span>
              Dashboard
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/applications"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              <span className="nav-icon">&#128196;</span>
              Applications
            </NavLink>
          </li>
        </ul>
      )}

      {!token && (
        <ul className="sidebar-nav">
          <li>
            <NavLink
              to="/login"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Login
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/register"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              Register
            </NavLink>
          </li>
        </ul>
      )}

      {token && (
        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout}>
            &#x23FB; Logout
          </button>
        </div>
      )}
    </nav>
  );
}
