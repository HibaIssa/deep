import UploadResume from "../components/UploadResume.jsx";

export default function Home() {
  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">
          RA
        </div>
        <div>
          <strong>Resume Advisor</strong>
          <span>Career intelligence dashboard</span>
        </div>
      </header>

      <section className="workspace">
        <div className="intro">
          <p className="eyebrow">Resume Career Advisor</p>
          <h1>Analyze a resume against a target role</h1>
          <p>
            Upload a PDF, DOCX, or TXT resume to extract skills, detect gaps, and generate a focused
            improvement report.
          </p>
          <div className="pipeline-strip" aria-label="Analysis pipeline">
            <span>Upload</span>
            <span>Extract</span>
            <span>Match</span>
            <span>Report</span>
          </div>
        </div>
        <UploadResume />
      </section>
    </main>
  );
}
