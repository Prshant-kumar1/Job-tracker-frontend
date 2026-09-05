import axios from "axios";

const BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach Bearer token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-redirect to login on 401 responses (expired/invalid token)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect if we're already on login/register
      const path = window.location.pathname;
      if (path !== "/login" && path !== "/register") {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Extract a user-friendly error message from an API error response.
 * Handles both the standard FastAPI format and custom validation format.
 */
export function getErrorMessage(err, fallback = "An error occurred.") {
  const data = err.response?.data;
  if (!data) return fallback;

  // Custom validation handler returns { detail: "Validation error", errors: [...] }
  if (data.errors && Array.isArray(data.errors)) {
    return data.errors.join(", ");
  }

  // Standard FastAPI validation: detail is an array of { msg, loc, type }
  if (Array.isArray(data.detail)) {
    return data.detail.map((d) => d.msg).join(", ");
  }

  // Simple string detail
  if (typeof data.detail === "string") {
    return data.detail;
  }

  return fallback;
}

// ── Auth ────────────────────────────────────────────────────────────────────
export const register = (data) => api.post("/auth/register", data);
export const login = (data) => api.post("/auth/login", data);

// ── Applications ────────────────────────────────────────────────────────────
export const getApplications = (status, pageSize) =>
  api.get("/applications", {
    params: {
      ...(status ? { status } : {}),
      ...(pageSize ? { page_size: Math.min(pageSize, 100) } : {}),
    },
  });

export const getApplication = (id) => api.get(`/applications/${id}`);

export const createApplication = (data) => api.post("/applications", data);

export const updateApplication = (id, data) =>
  api.put(`/applications/${id}`, data);

export const deleteApplication = (id) => api.delete(`/applications/${id}`);

// ── Dashboard ───────────────────────────────────────────────────────────────
export const getDashboardSummary = () => api.get("/dashboard/summary");

// ── AI ───────────────────────────────────────────────────────────────────────
export const getAiSuggestion = (applicationId) =>
  api.post(`/ai/suggest/${applicationId}`);

export default api;

