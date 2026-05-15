import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import FinalReport from "./FinalReport.jsx";

const report = {
  selected_role: "Backend Developer",
  predicted_role: {
    role: "Pending model integration",
    confidence: 0,
    model: "external_model_placeholder",
  },
  extracted_skills: [{ skill: "python", source: "keyword", score: 1 }],
  gap_analysis: {
    target_role: "Backend Developer",
    required_skills: ["python", "fastapi"],
    matched_skills: ["python"],
    missing_skills: ["fastapi"],
    coverage_percent: 50,
  },
  recommendations: [
    {
      title: "Close skill gaps",
      detail: "Practice FastAPI with a small project.",
      priority: "High",
    },
  ],
};

describe("FinalReport", () => {
  it("renders a user-oriented summary and recommendations", () => {
    render(<FinalReport report={report} />);

    expect(screen.getAllByText("50%").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Backend Developer").length).toBeGreaterThan(0);
    expect(screen.getByText(/Close skill gaps/)).toBeInTheDocument();
  });
});
