import unittest

from proxylens.models import DiagnosticReport, Finding, Status


class ModelTests(unittest.TestCase):
    def test_score_has_floor(self) -> None:
        report = DiagnosticReport(
            [Finding(str(index), "test", Status.ERROR, "bad") for index in range(10)]
        )
        self.assertEqual(report.score, 0)

    def test_clean_report_headline(self) -> None:
        report = DiagnosticReport([Finding("dns", "DNS", Status.OK, "ok")])
        self.assertEqual(report.headline, "暂未发现明显问题")


if __name__ == "__main__":
    unittest.main()
