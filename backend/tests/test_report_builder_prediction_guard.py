import unittest

from app.services.report_builder import _flag_low_evidence_prediction


class PredictionGuardTests(unittest.TestCase):
    def test_hides_prediction_when_role_has_weak_evidence(self):
        prediction = {
            "role": "Data Scientist",
            "confidence": 0.8,
            "model": "distilbert_resume_job_classifier",
        }

        guarded = _flag_low_evidence_prediction(
            prediction,
            {
                "matched_count": 1,
                "coverage_percent": 5.0,
            },
        )

        self.assertEqual(guarded["role"], "Cannot decide")
        self.assertEqual(guarded["confidence"], 0.0)
        self.assertEqual(guarded["raw_role"], "Data Scientist")
        self.assertTrue(guarded["low_evidence"])

    def test_keeps_prediction_when_role_has_enough_evidence(self):
        prediction = {
            "role": "Data Scientist",
            "confidence": 0.8,
            "model": "distilbert_resume_job_classifier",
        }

        guarded = _flag_low_evidence_prediction(
            prediction,
            {
                "matched_count": 4,
                "coverage_percent": 35.0,
            },
        )

        self.assertEqual(guarded, prediction)


if __name__ == "__main__":
    unittest.main()
