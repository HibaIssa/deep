import { Download, FileCheck2, FileText, Loader2, Save, Sparkles, UploadCloud } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import FinalReport from "./FinalReport.jsx";
import {
  exportReportPdf,
  fetchRoles,
  fetchSavedReport,
  fetchSavedReports,
  generateReport,
  loginUser,
  registerUser,
  saveReport,
} from "../services/api.js";

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState("");
  const [report, setReport] = useState(null);
  const [auth, setAuth] = useState(() => {
    const saved = localStorage.getItem("resumeAdvisorAuth");
    return saved ? JSON.parse(saved) : null;
  });
  const [savedReports, setSavedReports] = useState([]);
  const [authForm, setAuthForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const tokenPreview = useMemo(() => {
    if (!report?.preprocessing?.tokens?.length) {
      return [];
    }
    return report.preprocessing.tokens.slice(0, 40);
  }, [report]);

  useEffect(() => {
    let ignore = false;

    fetchRoles()
      .then((loadedRoles) => {
        if (ignore) {
          return;
        }
        setRoles(loadedRoles);
        setSelectedRole(loadedRoles[0] || "");
      })
      .catch((roleError) => setError(roleError.message));

    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    if (!auth?.token) {
      setSavedReports([]);
      return;
    }

    fetchSavedReports(auth.token)
      .then(setSavedReports)
      .catch((savedError) => setError(savedError.message));
  }, [auth]);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Choose a resume file first.");
      return;
    }

    setIsUploading(true);
    setError("");
    setReport(null);

    try {
      const payload = await generateReport(file, selectedRole);
      setReport(payload);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setIsUploading(false);
    }
  }

  async function handleAuth(mode) {
    setError("");
    try {
      const payload =
        mode === "register"
          ? await registerUser(authForm.username, authForm.password)
          : await loginUser(authForm.username, authForm.password);
      localStorage.setItem("resumeAdvisorAuth", JSON.stringify(payload));
      setAuth(payload);
      setAuthForm({ username: "", password: "" });
    } catch (authError) {
      setError(authError.message);
    }
  }

  async function handleSaveReport() {
    if (!auth?.token || !report) {
      setError("Log in before saving a report.");
      return;
    }

    setIsSaving(true);
    setError("");
    try {
      await saveReport(auth.token, `${report.selected_role} report`, report);
      setSavedReports(await fetchSavedReports(auth.token));
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setIsSaving(false);
    }
  }

  async function handleOpenSaved(reportId) {
    setError("");
    try {
      setReport(await fetchSavedReport(auth.token, reportId));
    } catch (savedError) {
      setError(savedError.message);
    }
  }

  async function handleExportPdf() {
    if (!report) {
      return;
    }

    setError("");
    try {
      const blob = await exportReportPdf(report);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "resume-career-report.pdf";
      link.click();
      URL.revokeObjectURL(url);
    } catch (pdfError) {
      setError(pdfError.message);
    }
  }

  return (
    <div className="upload-layout">
      <form className="upload-panel" onSubmit={handleSubmit}>
        <div className="panel-heading">
          <div className="icon-tile">
            <UploadCloud size={20} aria-hidden="true" />
          </div>
          <div>
            <h2>Resume input</h2>
            <p>Choose a resume and target role.</p>
          </div>
        </div>

        <label className="drop-zone">
          {file ? <FileCheck2 size={36} aria-hidden="true" /> : <UploadCloud size={36} aria-hidden="true" />}
          <span>{file ? file.name : "Select resume file"}</span>
          <small>PDF, DOCX, or TXT up to 5 MB</small>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
        </label>

        <label className="field">
          <span>Target role</span>
          <select value={selectedRole} onChange={(event) => setSelectedRole(event.target.value)}>
            {roles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </label>

        <button className="primary-button" type="submit" disabled={isUploading}>
          {isUploading ? <Loader2 className="spin" size={18} /> : <Sparkles size={18} />}
          <span>{isUploading ? "Generating" : "Generate report"}</span>
        </button>

        <div className="auth-panel">
          {auth ? (
            <>
              <div>
                <strong>{auth.username}</strong>
                <span>Saved reports enabled</span>
              </div>
              <button
                className="secondary-button"
                type="button"
                onClick={() => {
                  localStorage.removeItem("resumeAdvisorAuth");
                  setAuth(null);
                }}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <input
                placeholder="Username"
                value={authForm.username}
                onChange={(event) => setAuthForm({ ...authForm, username: event.target.value })}
              />
              <input
                placeholder="Password"
                type="password"
                value={authForm.password}
                onChange={(event) => setAuthForm({ ...authForm, password: event.target.value })}
              />
              <div className="auth-actions">
                <button type="button" onClick={() => handleAuth("login")}>
                  Log in
                </button>
                <button type="button" onClick={() => handleAuth("register")}>
                  Register
                </button>
              </div>
            </>
          )}
        </div>

        {savedReports.length > 0 && (
          <div className="saved-list">
            <h2>Saved reports</h2>
            {savedReports.slice(0, 4).map((item) => (
              <button type="button" key={item.id} onClick={() => handleOpenSaved(item.id)}>
                <span>{item.title}</span>
                <strong>{item.coverage_percent}%</strong>
              </button>
            ))}
          </div>
        )}

        {error && <p className="error-message">{error}</p>}
      </form>

      <section className="result-panel" aria-live="polite">
        {!report ? (
          <div className="empty-state">
            <div className="empty-visual" aria-hidden="true">
              <FileText size={32} />
              <span />
              <span />
              <span />
            </div>
            <h2>Ready for analysis</h2>
            <p>Upload a resume to see role alignment, skills, gaps, and recommendations.</p>
          </div>
        ) : (
          <div className="result-content">
            <div className="report-actions">
              <button className="secondary-button" type="button" onClick={handleExportPdf}>
                <Download size={17} />
                <span>PDF</span>
              </button>
              <button className="secondary-button" type="button" onClick={handleSaveReport} disabled={isSaving}>
                {isSaving ? <Loader2 className="spin" size={17} /> : <Save size={17} />}
                <span>{isSaving ? "Saving" : "Save"}</span>
              </button>
            </div>

            <FinalReport report={report} />

            <div className="stats-grid">
              <Metric label="Tokens" value={report.preprocessing.stats.token_count} />
              <Metric label="Unique" value={report.preprocessing.stats.unique_token_count} />
              <Metric label="Coverage" value={`${report.gap_analysis.coverage_percent}%`} />
            </div>

            <div>
              <h2>Token preview</h2>
              <div className="token-list">
                {tokenPreview.map((token, index) => (
                  <span key={`${token}-${index}`}>{token}</span>
                ))}
              </div>
            </div>

            <div>
              <h2>Processed text</h2>
              <p className="processed-text">{report.preprocessing.processed_text}</p>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
