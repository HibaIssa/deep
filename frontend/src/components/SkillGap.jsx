export default function SkillGap({ gapAnalysis, extractedSkills }) {
  const matchedCount = gapAnalysis.matched_skills.length;
  const missingCount = gapAnalysis.missing_skills.length;
  const waivedSkills = gapAnalysis.waived_skills || [];
  const waivedCount = waivedSkills.length;
  const totalSkills = Math.max(gapAnalysis.required_skills.length, 1);
  const matchedPercent = Math.round(gapAnalysis.coverage_percent);
  const missingPercent = Math.round((missingCount / totalSkills) * 100);
  const waivedPercent = Math.round((waivedCount / totalSkills) * 100);

  return (
    <section className="report-section">
      <div className="section-heading">
        <h2>Skill gap</h2>
        <span>{gapAnalysis.coverage_percent}% covered</span>
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <h3>Required skills coverage</h3>
          <div className="stacked-bar" aria-label={`${matchedPercent}% matched and ${missingPercent}% missing`}>
            <span className="bar-matched" style={{ width: `${matchedPercent}%` }} />
            {waivedCount > 0 && <span className="bar-waived" style={{ width: `${waivedPercent}%` }} />}
            <span className="bar-missing" style={{ width: `${missingPercent}%` }} />
          </div>
          <div className="chart-legend">
            <span><i className="legend matched" /> Matched {matchedCount}</span>
            {waivedCount > 0 && <span><i className="legend waived" /> Alternatives {waivedCount}</span>}
            <span><i className="legend missing" /> Missing {missingCount}</span>
          </div>
        </div>

        <div className="chart-card">
          <h3>Readiness breakdown</h3>
          <div className="mini-bars">
            <ChartBar label="Matched" value={matchedPercent} tone="matched" />
            {waivedCount > 0 && <ChartBar label="Alternatives" value={waivedPercent} tone="waived" />}
            <ChartBar label="Missing" value={missingPercent} tone="missing" />
          </div>
        </div>
      </div>

      <div className="two-column">
        <SkillList title="Matched skills" items={gapAnalysis.matched_skills} tone="matched" />
        <SkillList title="Missing skills" items={gapAnalysis.missing_skills} tone="missing" />
      </div>
      {waivedCount > 0 && (
        <SkillList
          title="Covered by alternatives"
          items={waivedSkills.map((item) => item.skill)}
          tone="waived"
        />
      )}

      <div>
        <div className="section-heading compact">
          <h2>Extracted skills</h2>
          <span>{extractedSkills.length} found</span>
        </div>
        <div className="skill-table">
          {extractedSkills.map((item) => (
            <div key={item.skill} className="skill-row">
              <div>
                <strong>{item.skill}</strong>
                <small>{item.source}</small>
              </div>
              <div className="skill-meter" aria-label={`${item.skill} confidence ${Math.round(item.score * 100)}%`}>
                <span style={{ width: `${Math.round(item.score * 100)}%` }} />
              </div>
              <span>{Math.round(item.score * 100)}%</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ChartBar({ label, value, tone }) {
  return (
    <div className="chart-bar-row">
      <div>
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className={`chart-bar ${tone}`}>
        <span style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function SkillList({ title, items, tone }) {
  return (
    <div>
      <h2>{title}</h2>
      <div className="token-list">
        {items.length ? (
          items.map((skill) => (
            <span className={tone} key={skill}>
              {skill}
            </span>
          ))
        ) : (
          <p className="muted">None</p>
        )}
      </div>
    </div>
  );
}
