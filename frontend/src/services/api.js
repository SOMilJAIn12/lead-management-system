/**
 * api.js
 * ------
 * Centralized axios client + functions for talking to the FastAPI backend.
 * Keeping all HTTP calls here (instead of scattered through components)
 * makes the base URL, error handling, and endpoints easy to manage in one
 * place.
 */
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

/**
 * Submit a new lead from the Lead Capture Form.
 * Throws an Error with a human-readable message on failure so the form
 * component can display it directly.
 */
export async function createLead(leadData) {
  try {
    const response = await apiClient.post("/lead", leadData);
    return response.data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

/** Fetch all leads, optionally filtered by a search term. */
export async function fetchLeads(search = "") {
  try {
    const response = await apiClient.get("/leads", {
      params: search ? { search } : {},
    });
    return response.data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

/** Fetch aggregated dashboard stats. */
export async function fetchDashboard() {
  try {
    const response = await apiClient.get("/dashboard");
    return response.data;
  } catch (err) {
    throw new Error(extractErrorMessage(err));
  }
}

/** Pulls the clearest possible message out of an axios/FastAPI error response. */
function extractErrorMessage(err) {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    // FastAPI/Pydantic validation error array
    return detail.map((d) => d.msg).join(", ");
  }
  if (typeof detail === "string") return detail;
  if (err?.message) return err.message;
  return "Something went wrong. Please try again.";
}

export { API_URL };
