const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function fetchRoles() {
  const response = await fetch(`${API_BASE_URL}/api/report/roles`);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Could not load job roles.");
  }
  return payload.roles;
}

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/resume/upload`, {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Resume upload failed.");
  }

  return payload;
}

export async function generateReport(file, selectedRole) {
  const formData = new FormData();
  formData.append("file", file);
  if (selectedRole) {
    formData.append("selected_role", selectedRole);
  }

  const response = await fetch(`${API_BASE_URL}/api/report/generate`, {
    method: "POST",
    body: formData,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Report generation failed.");
  }

  return payload;
}

export async function registerUser(username, password) {
  return authRequest("/api/auth/register", username, password);
}

export async function loginUser(username, password) {
  return authRequest("/api/auth/login", username, password);
}

export async function exportReportPdf(report) {
  const response = await fetch(`${API_BASE_URL}/api/report/export-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });

  if (!response.ok) {
    const payload = await response.json();
    throw new Error(payload.detail || "PDF export failed.");
  }

  return response.blob();
}

export async function saveReport(token, title, report) {
  const response = await fetch(`${API_BASE_URL}/api/report/saved`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ title, report }),
  });

  return parseJsonResponse(response, "Could not save report.");
}

export async function fetchSavedReports(token) {
  const response = await fetch(`${API_BASE_URL}/api/report/saved`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  return parseJsonResponse(response, "Could not load saved reports.");
}

export async function fetchSavedReport(token, reportId) {
  const response = await fetch(`${API_BASE_URL}/api/report/saved/${reportId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  return parseJsonResponse(response, "Could not open saved report.");
}

async function authRequest(path, username, password) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  return parseJsonResponse(response, "Authentication failed.");
}

async function parseJsonResponse(response, fallbackMessage) {
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || fallbackMessage);
  }
  return payload;
}
