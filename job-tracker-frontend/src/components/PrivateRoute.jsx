import { Navigate } from "react-router-dom";

function isTokenExpired(token) {
  if (!token) return true;
  try {
    const payloadBase64 = token.split(".")[1];
    const decodedJson = atob(payloadBase64.replace(/-/g, "+").replace(/_/g, "/"));
    const payload = JSON.parse(decodedJson);
    // exp is in seconds, Date.now() is in ms
    return payload.exp * 1000 < Date.now();
  } catch (e) {
    return true; // if token is malformed, consider it expired
  }
}

export default function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  if (!token || isTokenExpired(token)) {
    if (token) {
      localStorage.removeItem("token");
      window.dispatchEvent(new Event("storage"));
    }
    return <Navigate to="/login" replace />;
  }
  return children;
}
