from __future__ import annotations

import argparse
import sys

from .checks import run_diagnostics
from .report import render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="检查常见的网络与代理问题")
    parser.add_argument("--show-private", action="store_true", help="报告中保留本机 IP 等信息")
    parser.add_argument("--output", "-o", help="将报告写入指定文件")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_diagnostics()
    text = render_text(report, private=not args.show_private)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
        print(f"报告已保存到 {args.output}")
    else:
        print(text)
    return 1 if any(item.status.value == "异常" for item in report.findings) else 0


if __name__ == "__main__":
    sys.exit(main())

