import unittest

from proxylens.models import DiagnosticReport, Finding, Status
from proxylens.report import redact, render_text


class ReportTests(unittest.TestCase):
    def test_redact_ipv4_and_url_credentials(self) -> None:
        text = "IP 192.168.1.12 proxy http://alice:secret@127.0.0.1:7890"
        result = redact(text)
        self.assertNotIn("192.168.1.12", result)
        self.assertNotIn("alice:secret", result)
        self.assertEqual(result.count("x.x.x.x"), 2)

    def test_redact_common_secret_fields(self) -> None:
        self.assertNotIn("abc123", redact("api_key=abc123"))
        self.assertNotIn("hunter2", redact("password: hunter2"))

    def test_report_headline_and_render(self) -> None:
        report = DiagnosticReport([Finding("dns", "DNS 解析", Status.ERROR, "失败")])
        self.assertIn("1 项异常", report.headline)
        self.assertIn("DNS 解析", render_text(report))


if __name__ == "__main__":
    unittest.main()
