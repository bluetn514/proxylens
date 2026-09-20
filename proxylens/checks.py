from __future__ import annotations

import os
import platform
import socket
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable

from .models import DiagnosticReport, Finding, Status

ProgressCallback = Callable[[str], None]

DNS_HOSTS = ("github.com", "www.microsoft.com")
TCP_TARGETS = (("github.com", 443), ("www.microsoft.com", 443))
LOCAL_PROXY_PORTS = (7890, 7891, 1080, 10808, 10809, 8080)


def _run(command: list[str], timeout: float = 5.0) -> tuple[int, str]:
    try:
        flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            creationflags=flags,
            check=False,
        )
        return result.returncode, (result.stdout or result.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return -1, str(exc)


def check_system() -> Finding:
    system = platform.system()
    release = platform.release()
    status = Status.OK if system == "Windows" else Status.INFO
    note = "当前系统支持全部检测项" if system == "Windows" else "非 Windows 系统会跳过部分代理检测"
    return Finding("system", "运行环境", status, f"{system} {release}", note)


def _windows_proxy() -> tuple[bool | None, str]:
    if platform.system() != "Windows":
        return None, ""
    try:
        import winreg

        path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
            enabled = bool(winreg.QueryValueEx(key, "ProxyEnable")[0])
            try:
                server = str(winreg.QueryValueEx(key, "ProxyServer")[0])
            except FileNotFoundError:
                server = ""
            return enabled, server
    except OSError:
        return None, ""


def check_proxy() -> Finding:
    env_values = {
        key: os.environ.get(key, "")
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY")
        if os.environ.get(key)
    }
    enabled, server = _windows_proxy()
    sources: list[str] = []
    if enabled:
        sources.append("Windows 系统代理：已开启")
    if env_values:
        sources.append("环境变量：" + ", ".join(sorted(env_values)))
    if enabled is None and platform.system() == "Windows":
        return Finding("proxy", "代理设置", Status.WARN, "无法读取系统代理", suggestion="尝试以普通用户重新运行")
    if sources:
        return Finding("proxy", "代理设置", Status.OK, "检测到代理配置", "；".join(sources))
    return Finding(
        "proxy",
        "代理设置",
        Status.INFO,
        "没有检测到系统代理",
        "如果正在使用 TUN 模式，这通常是正常的。",
    )


def check_winhttp_proxy() -> Finding:
    if platform.system() != "Windows":
        return Finding("winhttp", "WinHTTP 代理", Status.INFO, "仅在 Windows 上检测")
    code, output = _run(["netsh", "winhttp", "show", "proxy"])
    if code != 0:
        return Finding("winhttp", "WinHTTP 代理", Status.WARN, "读取失败", output[:240])
    direct_markers = ("Direct access", "直接访问")
    direct = any(marker.lower() in output.lower() for marker in direct_markers)
    if direct:
        return Finding("winhttp", "WinHTTP 代理", Status.OK, "当前为直连")
    return Finding(
        "winhttp",
        "WinHTTP 代理",
        Status.WARN,
        "检测到单独的 WinHTTP 代理",
        "为避免泄露代理地址，报告不显示具体服务器。",
        "如果应用关闭后仍无法联网，可检查这里是否残留旧配置。",
    )


def check_dns(hosts: Iterable[str] = DNS_HOSTS) -> Finding:
    results: list[str] = []
    failures: list[str] = []
    for host in hosts:
        started = time.perf_counter()
        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
            elapsed = (time.perf_counter() - started) * 1000
            families = []
            if any(":" not in address for address in addresses):
                families.append("IPv4")
            if any(":" in address for address in addresses):
                families.append("IPv6")
            results.append(f"{host} {elapsed:.0f} ms ({'/'.join(families) or '未知'})")
        except OSError as exc:
            failures.append(f"{host}: {exc}")
    if failures and not results:
        return Finding("dns", "DNS 解析", Status.ERROR, "域名均无法解析", "；".join(failures), "尝试更换 DNS 或暂时关闭代理后重试。")
    if failures:
        return Finding("dns", "DNS 解析", Status.WARN, "部分域名解析失败", "；".join(results + failures))
    return Finding("dns", "DNS 解析", Status.OK, "解析正常", "；".join(results))


def check_tcp(targets: Iterable[tuple[str, int]] = TCP_TARGETS) -> Finding:
    successes: list[str] = []
    failures: list[str] = []
    for host, port in targets:
        started = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=4):
                elapsed = (time.perf_counter() - started) * 1000
                successes.append(f"{host}:{port} {elapsed:.0f} ms")
        except OSError as exc:
            failures.append(f"{host}:{port} ({exc})")
    if not successes:
        return Finding("tcp", "HTTPS 连接", Status.ERROR, "测试站点均无法建立连接", "；".join(failures), "检查防火墙、代理节点或校园网登录状态。")
    if failures:
        return Finding("tcp", "HTTPS 连接", Status.WARN, "部分站点连接失败", "；".join(successes + failures))
    return Finding("tcp", "HTTPS 连接", Status.OK, "连接正常", "；".join(successes))


def check_http() -> Finding:
    request = urllib.request.Request(
        "https://www.microsoft.com/favicon.ico",
        headers={"User-Agent": "ProxyLens/0.1"},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            response.read(1024)
            elapsed = (time.perf_counter() - started) * 1000
            return Finding("http", "网页访问", Status.OK, f"HTTPS 请求成功，{elapsed:.0f} ms", f"HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        return Finding("http", "网页访问", Status.WARN, f"服务器返回 HTTP {exc.code}", str(exc))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return Finding("http", "网页访问", Status.ERROR, "HTTPS 请求失败", str(exc), "如果端口能连接但网页打不开，重点检查代理规则和证书。")


def check_local_proxy_ports(ports: Iterable[int] = LOCAL_PROXY_PORTS) -> Finding:
    opened: list[int] = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.12)
        try:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                opened.append(port)
        finally:
            sock.close()
    if opened:
        return Finding("ports", "本地代理端口", Status.OK, "发现正在监听的常用端口", ", ".join(map(str, opened)))
    return Finding("ports", "本地代理端口", Status.INFO, "未发现常用代理端口", "TUN 模式或自定义端口不会出现在这里。")


CHECKS = (
    check_system,
    check_proxy,
    check_winhttp_proxy,
    check_local_proxy_ports,
    check_dns,
    check_tcp,
    check_http,
)


def run_diagnostics(progress: ProgressCallback | None = None) -> DiagnosticReport:
    report = DiagnosticReport()
    for check in CHECKS:
        if progress:
            progress(check.__name__)
        try:
            report.add(check())
        except Exception as exc:  # A failed check should not stop the full report.
            report.add(Finding(check.__name__, "检测项", Status.WARN, "检测过程中出现问题", str(exc)))
    return report
