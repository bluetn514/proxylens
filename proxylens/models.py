from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Status(str, Enum):
    OK = "正常"
    WARN = "注意"
    ERROR = "异常"
    INFO = "信息"


@dataclass(frozen=True)
class Finding:
    key: str
    title: str
    status: Status
    summary: str
    detail: str = ""
    suggestion: str = ""


@dataclass
class DiagnosticReport:
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def extend(self, findings: Iterable[Finding]) -> None:
        self.findings.extend(findings)

    @property
    def score(self) -> int:
        penalties = {Status.ERROR: 25, Status.WARN: 10, Status.OK: 0, Status.INFO: 0}
        return max(0, 100 - sum(penalties[item.status] for item in self.findings))

    @property
    def headline(self) -> str:
        errors = sum(item.status == Status.ERROR for item in self.findings)
        warnings = sum(item.status == Status.WARN for item in self.findings)
        if errors:
            return f"发现 {errors} 项异常，建议先处理标红项目"
        if warnings:
            return f"网络基本可用，有 {warnings} 项值得留意"
        return "暂未发现明显问题"

