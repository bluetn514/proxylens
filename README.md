# ProxyLens

一个小型 Windows 网络诊断工具，用来检查系统代理、WinHTTP、DNS、本地代理端口和 HTTPS 连接。

它只读取当前网络状态，不会替你修改系统设置。适合在这些情况下先跑一遍：

- 代理软件开着，但浏览器或命令行无法联网
- 退出代理软件后，部分程序仍然走旧代理
- GitHub 等网站时好时坏
- 不确定问题出在 DNS、代理端口还是网络本身
- 想把诊断结果发给别人，又不希望直接暴露本机 IP

> 目前仍是早期版本。如果结果和实际情况不符，欢迎提交 issue，并附上已经脱敏的报告。

## 截图

首个 Windows Release 发布后补充。

## 下载

普通用户可以从仓库右侧的 **Releases** 下载 `ProxyLens.exe`。它是便携版，不需要安装。

首次运行时，Windows 可能显示来源未知提示。这是因为开源项目暂时没有购买代码签名证书。你可以先查看本仓库源码和自动构建配置，再决定是否运行。

仓库维护者首次发布时，可以在 Windows 上运行根目录的 `publish-to-github.ps1`。脚本会完成 GitHub 登录、首次推送和 `v0.1.0` 标签创建。

## 已有检查项

- Windows 系统代理
- 环境变量代理
- WinHTTP 代理残留
- 常见本地代理端口
- DNS 解析和耗时
- IPv4 / IPv6 解析情况
- 443 端口连接
- HTTPS 请求
- 复制或保存脱敏报告

复制报告时会隐藏 IPv4 地址、URL 中的用户名和密码，以及常见的 Token、Password、API Key 字段。自动脱敏无法覆盖所有情况，公开报告前仍应自己检查一遍。

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

## 本地构建

```powershell
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name ProxyLens proxylens_gui.py
```

仓库中的 GitHub Actions 会在 Windows 环境运行测试，并在创建 `v*` 标签时生成 Release 和便携版程序。

## 开发

```powershell
python -m pip install -e .
python -m unittest discover -s tests
```

项目尽量只使用 Python 标准库。新增检测项时请注意两件事：不要静默修改用户设置；不要把敏感信息写进报告。

## 计划

- 对比直连与系统代理的连接结果
- 检查 DNS 服务器配置
- 支持自定义测试站点
- 增加英文界面
- 为常见错误提供更具体的排查步骤

## License

[MIT](LICENSE)
