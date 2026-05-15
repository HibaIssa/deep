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
