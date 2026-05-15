import { FileCheck2, FileText, Loader2, Sparkles, UploadCloud } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import FinalReport from "./FinalReport.jsx";
import { fetchRoles, generateReport } from "../services/api.js";

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);

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
