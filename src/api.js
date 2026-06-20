import axios from "axios";

const BASE_URL =
  import.meta.env.VITE_API_URL || "https://job-tracker-api-dgs0.onrender.com";

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

// ── Auth ────────────────────────────────────────────────────────────────────
export const register = (data) => api.post("/auth/register", data);
export const login = (data) => api.post("/auth/login", data);

// ── Applications ────────────────────────────────────────────────────────────
export const getApplications = (status) =>
  api.get("/applications", { params: status ? { status } : {} });

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
