export default function RolePrediction({ predictedRole, selectedRole }) {
  const confidence = Math.round(predictedRole.confidence * 100);

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
          <span>Confidence</span>
          <strong>{confidence}%</strong>
        </div>
      </div>
      <div className="confidence-track" aria-label={`Model confidence ${confidence}%`}>
        <span style={{ width: `${confidence}%` }} />
      </div>
      {predictedRole.warning ? (
        <p className="prediction-warning">{predictedRole.warning}</p>
      ) : null}
    </section>
  );
}
