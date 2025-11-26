const BACKEND_URL = "http://localhost:8000";
export const getBackendURL = () => {
  return import.meta.env.BACKEND_URL ?? BACKEND_URL
}
