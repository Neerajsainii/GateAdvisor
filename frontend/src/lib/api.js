import axios from "axios";

const DEFAULT_API_BASE_URL = import.meta.env.PROD
  ? "https://gate-advisor-backend.azurewebsites.net/api"
  : "http://localhost:8000/api";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
export const AUTH_TOKEN_STORAGE_KEY = "gate_advisor_auth_token";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
      Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});

function readStoredToken() {
  if (typeof window === "undefined") {
    return "";
  }
  return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) || "";
}

export function setAuthToken(token) {
  if (typeof window !== "undefined") {
    if (token) {
      window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
    } else {
      window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
    }
  }

  if (token) {
    api.defaults.headers.common.Authorization = `Token ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

setAuthToken(readStoredToken());

export async function loadRazorpayScript() {
  if (window.Razorpay) {
    return true;
  }

  return new Promise((resolve) => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}
