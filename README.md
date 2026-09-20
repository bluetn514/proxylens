# ProxyLens

一键检查 Windows 代理、DNS 和 HTTPS 连接问题。

[![Release](https://img.shields.io/github/v/release/bluetn514/proxylens?display_name=tag&style=flat-square)](https://github.com/bluetn514/proxylens/releases/latest)
[![Tests](https://img.shields.io/github/actions/workflow/status/bluetn514/proxylens/test.yml?branch=main&label=tests&style=flat-square)](https://github.com/bluetn514/proxylens/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/bluetn514/proxylens?style=flat-square)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/bluetn514/proxylens/total?style=flat-square)](https://github.com/bluetn514/proxylens/releases)

[下载 Windows 便携版](https://github.com/bluetn514/proxylens/releases/latest) · [English](README_EN.md) · [提交问题](https://github.com/bluetn514/proxylens/issues/new?template=bug_report.yml)

![ProxyLens 界面预览](assets/proxylens-preview.svg)

代理软件明明开着，浏览器或命令行却无法联网；退出软件后，部分程序仍然走旧代理；GitHub 时好时坏——ProxyLens 把常见检查集中在一个窗口里，先帮你判断问题更可能出在哪一层。

它只读取当前网络状态，不会修改代理、DNS 或其他系统设置。复制报告时会自动隐藏 IP、URL 凭据和常见 Token 字段，方便把结果发给别人协助排查。

## 能检查什么

- Windows 系统代理和环境变量代理
- WinHTTP 代理残留
- 常见本地代理端口
- DNS 解析、耗时及 IPv4 / IPv6
- 443 端口连接
- HTTPS 请求
- 一键复制或保存脱敏报告

## 下载与使用

1. 打开 [Releases](https://github.com/bluetn514/proxylens/releases/latest)，下载 `ProxyLens.exe`。
2. 双击运行，点击“开始检查”。它是便携版，不需要安装。
3. 如果需要求助，点击“复制报告”，检查内容后再发送。

首次运行时，Windows 可能显示来源未知提示。这是因为个人开源项目暂时没有代码签名证书。构建过程由 GitHub Actions 公开完成，也可以直接从源码运行。

## 从源码运行

需要 Python 3.9 或更高版本。

```powershell
git clone https://github.com/bluetn514/proxylens.git
cd proxylens
python -m proxylens.gui
```

命令行模式：

```powershell
python -m proxylens
python -m proxylens --output report.txt
```

## 隐私说明

ProxyLens 不上传诊断结果，也不会静默修改系统配置。

自动脱敏会处理 IPv4 地址、URL 中的用户名和密码，以及常见的 Token、Password、API Key 字段。但自动规则无法覆盖所有情况，公开报告前仍应自己检查一遍。请勿提交代理订阅、节点地址或任何账号凭据。

## 开发

```powershell
python -m pip install -e .
python -m unittest discover -s tests
```

项目尽量只使用 Python 标准库。新增检测项时请遵守两条原则：不要静默修改用户设置；不要把敏感信息写进报告。贡献方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 下一步

- 对比直连与系统代理的连接结果
- 检查 DNS 服务器配置
- 支持自定义测试站点
- 为常见错误提供更具体的排查步骤

如果它帮你少走了一点弯路，可以点一个 Star。遇到误判也欢迎直接开 Issue，真实案例比功能清单更有用。

## License

[MIT](LICENSE)
