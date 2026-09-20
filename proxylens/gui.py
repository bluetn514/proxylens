from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .checks import run_diagnostics
from .models import DiagnosticReport, Finding, Status
from .report import render_text

COLORS = {
    Status.OK: "#17803d",
    Status.WARN: "#a15c00",
    Status.ERROR: "#c52a2a",
    Status.INFO: "#536471",
}
LABELS = {
    "check_system": "读取系统信息",
    "check_proxy": "检查代理设置",
    "check_winhttp_proxy": "检查 WinHTTP",
    "check_local_proxy_ports": "检查本地端口",
    "check_dns": "测试 DNS",
    "check_tcp": "测试 HTTPS 连接",
    "check_http": "测试网页访问",
}


class ProxyLensApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ProxyLens")
        self.geometry("780x620")
        self.minsize(680, 520)
        self.configure(bg="#f5f7fa")
        self.report: DiagnosticReport | None = None
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self._build_style()
        self._build_ui()
        self.after(80, self._drain_events)

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("vista")
        except tk.TclError:
            style.theme_use("clam")
        style.configure("Primary.TButton", font=("Microsoft YaHei UI", 10, "bold"), padding=(18, 10))
        style.configure("Quiet.TButton", font=("Microsoft YaHei UI", 9), padding=(12, 8))

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg="#172033", padx=28, pady=22)
        header.pack(fill="x")
        tk.Label(header, text="ProxyLens", font=("Segoe UI", 23, "bold"), fg="white", bg="#172033").pack(anchor="w")
        tk.Label(
            header,
            text="检查 Windows 上常见的网络和代理问题",
            font=("Microsoft YaHei UI", 10),
            fg="#cbd5e1",
            bg="#172033",
        ).pack(anchor="w", pady=(5, 0))

        actions = tk.Frame(self, bg="#f5f7fa", padx=28, pady=18)
        actions.pack(fill="x")
        self.start_button = ttk.Button(actions, text="开始检查", style="Primary.TButton", command=self.start_scan)
        self.start_button.pack(side="left")
        self.copy_button = ttk.Button(actions, text="复制报告", style="Quiet.TButton", state="disabled", command=self.copy_report)
        self.copy_button.pack(side="left", padx=(10, 0))
        self.save_button = ttk.Button(actions, text="保存报告", style="Quiet.TButton", state="disabled", command=self.save_report)
        self.save_button.pack(side="left", padx=(8, 0))
        self.progress = ttk.Progressbar(actions, mode="indeterminate", length=150)
        self.progress.pack(side="right")

        summary = tk.Frame(self, bg="white", highlightbackground="#e2e8f0", highlightthickness=1, padx=20, pady=15)
        summary.pack(fill="x", padx=28, pady=(0, 14))
        self.summary_title = tk.Label(summary, text="还没有开始检查", font=("Microsoft YaHei UI", 13, "bold"), fg="#172033", bg="white")
        self.summary_title.pack(anchor="w")
        self.summary_note = tk.Label(summary, text="整个过程通常需要十几秒，不会修改系统设置。", font=("Microsoft YaHei UI", 9), fg="#64748b", bg="white")
        self.summary_note.pack(anchor="w", pady=(5, 0))

        body = tk.Frame(self, bg="#f5f7fa")
        body.pack(fill="both", expand=True, padx=28, pady=(0, 22))
        self.canvas = tk.Canvas(body, bg="#f5f7fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.items = tk.Frame(self.canvas, bg="#f5f7fa")
        self.items.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.items, anchor="nw")
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.window_id, width=event.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def start_scan(self) -> None:
        self.start_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.progress.start(12)
        self.summary_title.configure(text="正在检查…", fg="#172033")
        self.summary_note.configure(text="读取系统网络状态")
        for child in self.items.winfo_children():
            child.destroy()
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self) -> None:
        report = run_diagnostics(lambda name: self.events.put(("progress", name)))
        self.events.put(("done", report))

    def _drain_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "progress":
                    self.summary_note.configure(text=LABELS.get(str(payload), "继续检查"))
                elif event == "done":
                    self._show_report(payload)  # type: ignore[arg-type]
        except queue.Empty:
            pass
        self.after(80, self._drain_events)

    def _show_report(self, report: DiagnosticReport) -> None:
        self.report = report
        self.progress.stop()
        self.start_button.configure(state="normal", text="重新检查")
        self.copy_button.configure(state="normal")
        self.save_button.configure(state="normal")
        self.summary_title.configure(text=report.headline, fg="#172033")
        self.summary_note.configure(text="以下结果仅用于排查，不会自动更改配置。")
        for finding in report.findings:
            self._add_finding(finding)

    def _add_finding(self, finding: Finding) -> None:
        card = tk.Frame(self.items, bg="white", highlightbackground="#e2e8f0", highlightthickness=1, padx=16, pady=13)
        card.pack(fill="x", pady=(0, 9))
        top = tk.Frame(card, bg="white")
        top.pack(fill="x")
        tk.Label(top, text=finding.status.value, font=("Microsoft YaHei UI", 9, "bold"), fg="white", bg=COLORS[finding.status], padx=8, pady=3).pack(side="left")
        tk.Label(top, text=finding.title, font=("Microsoft YaHei UI", 11, "bold"), fg="#1e293b", bg="white").pack(side="left", padx=(10, 0))
        tk.Label(card, text=finding.summary, font=("Microsoft YaHei UI", 9), fg="#334155", bg="white", justify="left", wraplength=650).pack(anchor="w", pady=(8, 0))
        if finding.detail:
            tk.Label(card, text=finding.detail, font=("Microsoft YaHei UI", 8), fg="#64748b", bg="white", justify="left", wraplength=650).pack(anchor="w", pady=(5, 0))
        if finding.suggestion:
            tk.Label(card, text="建议：" + finding.suggestion, font=("Microsoft YaHei UI", 8), fg="#7c3f00", bg="#fff8eb", padx=8, pady=5, justify="left", wraplength=640).pack(anchor="w", fill="x", pady=(8, 0))

    def copy_report(self) -> None:
        if not self.report:
            return
        self.clipboard_clear()
        self.clipboard_append(render_text(self.report, private=True))
        self.update()
        messagebox.showinfo("ProxyLens", "报告已复制。IP 和常见凭据字段已隐藏。")

    def save_report(self) -> None:
        if not self.report:
            return
        path = filedialog.asksaveasfilename(
            title="保存诊断报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")],
            initialfile="proxylens-report.txt",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(render_text(self.report, private=True) + "\n")
        messagebox.showinfo("ProxyLens", "报告已保存。")


def main() -> None:
    ProxyLensApp().mainloop()


if __name__ == "__main__":
    main()

