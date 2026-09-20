from __future__ import annotations

import re
from datetime import datetime, timezone

from .models import DiagnosticReport

_IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
_AUTH_URL = re.compile(r"(?P<scheme>https?://)(?P<auth>[^\s/@:]+:[^\s/@]+)@", re.IGNORECASE)
_TOKEN = re.compile(r"(?i)\b(token|password|passwd|secret|api[_-]?key)\s*[=:]\s*[^\s,;]+")


def redact(text: str) -> str:
    text = _AUTH_URL.sub(r"\g<scheme>***:***@", text)
    text = _TOKEN.sub(lambda match: f"{match.group(1)}=***", text)
    text = _IPV4.sub("x.x.x.x", text)
    return text


def render_text(report: DiagnosticReport, *, private: bool = True) -> str:
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    lines = ["ProxyLens 诊断报告", f"时间：{now}", f"结果：{report.headline}", ""]
    for item in report.findings:
        lines.append(f"[{item.status.value}] {item.title}：{item.summary}")
        if item.detail:
            lines.append(f"  详情：{item.detail}")
        if item.suggestion:
            lines.append(f"  建议：{item.suggestion}")
    lines.extend(["", "报告由 ProxyLens 生成。分享前仍建议快速检查一遍内容。"]) 
    output = "\n".join(lines)
    return redact(output) if private else output

