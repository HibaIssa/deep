export default function RolePrediction({ predictedRole, selectedRole }) {
  const confidenceValue = predictedRole.evidence_adjusted_confidence ?? predictedRole.confidence;
  const confidence = Math.round(confidenceValue * 100);

  return (
    <section className="report-section">
      <div className="section-heading">
        <h2>Role prediction</h2>
        <span>{predictedRole.model}</span>
      </div>
      <div className="role-row">
        <div>
          <span>Model result</span>
          <strong>{predictedRole.role}</strong>
        </div>
        <div>
          <span>Target role used</span>
          <strong>{selectedRole}</strong>
        </div>
        <div>
          <span>{predictedRole.low_evidence ? "Evidence confidence" : "Confidence"}</span>
          <strong>{confidence}%</strong>
        </div>
      </div>
      <div className="confidence-track" aria-label={`Model confidence ${confidence}%`}>
        <span style={{ width: `${confidence}%` }} />
      </div>
      {predictedRole.warning ? (
        <p className="prediction-warning">
          {predictedRole.warning}
          {predictedRole.confidence_note ? ` ${predictedRole.confidence_note}` : ""}
        </p>
      ) : null}
    </section>
  );
}
