import { AlertTriangle, CheckCircle2, Target, TrendingUp } from "lucide-react";

import RolePrediction from "./RolePrediction.jsx";
import SkillGap from "./SkillGap.jsx";

export default function FinalReport({ report }) {
  const coverage = report.gap_analysis.coverage_percent;
  const missingCount = report.gap_analysis.missing_skills.length;
  const matchedCount = report.gap_analysis.matched_skills.length;

  return (
    <>
      <section className="report-hero">
        <div className="score-card">
          <div
            className="score-ring"
            style={{ "--score": `${coverage}%` }}
            aria-label={`Career match score ${coverage}%`}
          >
            <strong>{coverage}%</strong>
            <span>Match</span>
          </div>
          <div>
            <p className="eyebrow">Career fit score</p>
            <h2>{getReadinessTitle(coverage)}</h2>
            <p>
              Your resume matches {matchedCount} required skills for {report.selected_role}.
              {missingCount ? ` Focus on ${missingCount} missing skills to improve fit.` : " You cover the core skills well."}
            </p>
          </div>
        </div>

        <div className="insight-grid">
          <Insight icon={<Target size={18} />} label="Target role" value={report.selected_role} />
          <Insight icon={<CheckCircle2 size={18} />} label="Matched" value={matchedCount} />
          <Insight icon={<AlertTriangle size={18} />} label="Missing" value={missingCount} />
          <Insight icon={<TrendingUp size={18} />} label="Next step" value={missingCount ? "Upskill" : "Polish"} />
        </div>
      </section>

      <RolePrediction predictedRole={report.predicted_role} selectedRole={report.selected_role} />

      <SkillGap gapAnalysis={report.gap_analysis} extractedSkills={report.extracted_skills} />

      <section className="report-section">
        <div className="section-heading">
          <h2>Recommendations</h2>
          <span>{report.recommendations.length} items</span>
        </div>
        <div className="recommendation-list">
          {report.recommendations.map((item, index) => (
            <article key={item.title} className="recommendation">
              <span>{item.priority}</span>
              <h3>{index + 1}. {item.title}</h3>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}

function Insight({ icon, label, value }) {
  return (
    <div className="insight-card">
      <div aria-hidden="true">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function getReadinessTitle(coverage) {
  if (coverage >= 80) {
    return "Strong role alignment";
  }
  if (coverage >= 55) {
    return "Good base with clear gaps";
  }
  return "Early fit, needs targeted upgrades";
}
