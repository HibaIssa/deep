import unittest

from app.services.gap_detection import detect_skill_gaps
from app.services.skill_extraction import extract_skills


class SkillGapDetectionTests(unittest.TestCase):
    def _gap_for(self, text: str, role: str) -> dict:
        extracted_skills = extract_skills(text, text)
        return detect_skill_gaps(extracted_skills, role, text)

    def test_backend_gap_detection_uses_extracted_and_phrase_matches(self):
        gap = self._gap_for(
            (
                "Built APIs with Python, FastAPI, SQL, Docker, pytest testing, "
                "system design, authentication, databases, and microservices."
            ),
            "Backend Developer",
        )

        self.assertIn("api design", gap["matched_skills"])
        self.assertIn("microservices", gap["matched_skills"])
        self.assertNotIn("api design", gap["missing_skills"])
        self.assertNotIn("microservices", gap["missing_skills"])
        self.assertGreaterEqual(gap["coverage_percent"], 80.0)
        self.assertTrue(gap["match_evidence"])

    def test_backend_framework_alternatives_are_not_counted_as_gaps(self):
        gap = self._gap_for(
            "Built production APIs using Python, FastAPI, SQL, PostgreSQL, Docker, and pytest.",
            "Backend Developer",
        )

        self.assertIn("fastapi", gap["matched_skills"])
        self.assertNotIn("node.js", gap["matched_skills"])
        self.assertNotIn("django", gap["matched_skills"])
        self.assertNotIn("node.js", gap["missing_skills"])
        self.assertNotIn("django", gap["missing_skills"])
        self.assertGreaterEqual(gap["coverage_percent"], 60.0)
        self.assertIn("node.js", {item["skill"] for item in gap["waived_skills"]})
        self.assertIn("django", {item["skill"] for item in gap["waived_skills"]})

    def test_inferred_matches_are_grounded_in_supporting_skills(self):
        gap = self._gap_for(
            "Built services with Python, FastAPI, PostgreSQL, Docker, and pytest.",
            "Backend Developer",
        )

        self.assertIn("api design", gap["matched_skills"])
        self.assertIn("databases", gap["matched_skills"])
        self.assertIn("testing", gap["matched_skills"])

        evidence_by_skill = {item["skill"]: item for item in gap["match_evidence"]}
        self.assertEqual(evidence_by_skill["api design"]["source"], "inferred")
        self.assertIn("fastapi", evidence_by_skill["api design"]["matched_alias"])

    def test_extraction_avoids_broad_design_and_testing_false_positives(self):
        extracted = extract_skills(
            "Built APIs with Python, FastAPI, SQL, Docker, pytest testing, and system design."
        )
        extracted_names = {item["skill"] for item in extracted}

        self.assertIn("python", extracted_names)
        self.assertIn("fastapi", extracted_names)
        self.assertIn("testing", extracted_names)
        self.assertNotIn("manual testing", extracted_names)
        self.assertNotIn("penetration testing", extracted_names)
        self.assertNotIn("responsive design", extracted_names)
        self.assertNotIn("ui design", extracted_names)

    def test_data_science_common_aliases_match(self):
        gap = self._gap_for(
            (
                "Experience with Python, ML, scikit learn, pandas, NumPy, "
                "dashboards in Tableau, A/B testing experiments, statistics, "
                "feature engineering, and model validation."
            ),
            "Data Scientist",
        )

        for skill in [
            "python",
            "machine learning",
            "data visualization",
            "pandas",
            "numpy",
            "scikit-learn",
            "experimentation",
            "statistics",
            "feature engineering",
            "model evaluation",
        ]:
            self.assertIn(skill, gap["matched_skills"])

    def test_partial_words_do_not_match_multi_word_required_skills(self):
        gap = self._gap_for(
            "Designed a public API. Created visual design patterns for frontend components.",
            "Software Engineer",
        )

        self.assertNotIn("api design", gap["matched_skills"])
        self.assertNotIn("system design", gap["matched_skills"])
        self.assertNotIn("software architecture", gap["matched_skills"])
        self.assertIn("design patterns", gap["matched_skills"])

    def test_devops_aliases_match(self):
        gap = self._gap_for(
            "AWS, Google Cloud Platform, k8s, CICD, IaC Terraform, Linux scripting, monitoring, and Docker.",
            "DevOps/Cloud Engineer",
        )

        for skill in [
            "aws",
            "gcp",
            "kubernetes",
            "ci/cd",
            "infrastructure as code",
            "terraform",
            "linux",
            "scripting",
            "monitoring",
            "docker",
        ]:
            self.assertIn(skill, gap["matched_skills"])

        self.assertNotIn("azure", gap["missing_skills"])

    def test_software_engineer_resume_uses_project_and_coursework_context(self):
        resume_text = (
            "Software Engineer and AI full-stack developer. Built mobile applications using React Native "
            "and full e-commerce platforms. Designed backend APIs using Node.js, Express, and .NET. "
            "Built scalable frontend systems using Next.js, React, and Tailwind CSS. "
            "B.Sc. Computer Science. Projects include a bookstore e-commerce full-stack system, "
            "a Django-based club management system, fraud detection, and AI assistants. "
            "Skills: Python, JavaScript, TypeScript, C++, Java, React, Node.js, Django, TensorFlow, "
            "NumPy, pandas, scikit-learn, Git, AWS, Docker, Postman."
        )

        extracted = extract_skills(resume_text, resume_text)
        extracted_names = {item["skill"] for item in extracted}
        gap = detect_skill_gaps(extracted, "Software Engineer", resume_text)

        self.assertNotIn("mobile ui", extracted_names)
        self.assertNotIn("web performance", extracted_names)

        for skill in [
            "data structures",
            "algorithms",
            "object-oriented programming",
            "system design",
            "api design",
            "git",
            "testing",
            "software architecture",
        ]:
            self.assertIn(skill, gap["matched_skills"])

        self.assertEqual(
            set(gap["missing_skills"]),
            {"debugging", "design patterns", "code review", "agile"},
        )
        self.assertGreaterEqual(gap["coverage_percent"], 60.0)


if __name__ == "__main__":
    unittest.main()
