const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const DEFAULT_ROLES = [
  "Software Engineer",
  "Frontend Developer",
  "Database Engineer",
  "DevOps/Cloud Engineer",
  "QA Engineer",
  "Data Scientist",
  "Cybersecurity Engineer",
  "AI/ML Engineer",
  "Data Engineer",
  "Full Stack Developer",
  "Backend Developer",
  "Blockchain Developer",
  "Mobile Developer",
];

export async function fetchRoles() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/report/roles`);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Could not load job roles.");
    }

    return Array.isArray(payload.roles) && payload.roles.length ? payload.roles : DEFAULT_ROLES;
  } catch (error) {
    console.warn("Using default roles because the API role list could not be loaded.", error);
    return DEFAULT_ROLES;
  }
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
