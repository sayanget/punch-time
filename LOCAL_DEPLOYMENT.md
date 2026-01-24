# 本地部署指南

本指南将帮助您在本地快速部署和运行打卡计时器应用。

## 快速开始 ⚡

### Windows用户

双击运行 `deploy.bat` 即可!

```batch
deploy.bat
```

### macOS/Linux用户

运行Python部署脚本:

```bash
python deploy.py
```

或者:

```bash
python3 deploy.py
```

## 详细说明

### 系统要求

- **Python**: 3.8或更高版本
- **操作系统**: Windows, macOS, 或 Linux
- **浏览器**: Chrome, Firefox, Safari, 或 Edge

### 部署脚本功能

部署脚本会自动完成以下步骤:

1. ✅ **检查Python环境** - 验证Python版本是否满足要求
2. ✅ **安装依赖包** - 自动安装所需的Python包
3. ✅ **生成SSL证书** - 创建自签名证书用于HTTPS
4. ✅ **初始化数据库** - 创建SQLite数据库
5. ✅ **启动服务器** - 启动HTTPS服务器并自动打开浏览器

### 首次运行

第一次运行时,脚本会:

1. 检查并安装所有依赖包(可能需要几分钟)
2. 生成SSL证书文件(保存在`ssl/`目录)
3. 创建数据库目录(`data/`)
4. 启动服务器并在浏览器中打开应用

### 访问应用

服务器启动后,浏览器会自动打开:

```
https://localhost:7778
```

> **注意**: 由于使用自签名证书,浏览器会显示安全警告。这是正常现象。

#### 处理安全警告

**Chrome/Edge**:
1. 点击"高级"或"Advanced"
2. 点击"继续访问localhost"或"Proceed to localhost"

**Firefox**:
1. 点击"高级"
2. 点击"接受风险并继续"

**Safari**:
1. 点击"显示详细信息"
2. 点击"访问此网站"

### 停止服务器

在终端/命令提示符中按 `Ctrl+C` 停止服务器。

## 手动部署步骤

如果您想手动部署,可以按照以下步骤操作:

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 生成SSL证书

```bash
python generate_ssl_cert.py
```

### 3. 启动HTTPS服务器

**Windows (PowerShell)**:
```powershell
$env:SSL_ENABLED="true"
$env:SSL_CERT_PATH="ssl/cert.pem"
$env:SSL_KEY_PATH="ssl/key.pem"
$env:HTTPS_PORT="7778"
python app.py
```

**macOS/Linux (Bash)**:
```bash
export SSL_ENABLED=true
export SSL_CERT_PATH=ssl/cert.pem
export SSL_KEY_PATH=ssl/key.pem
export HTTPS_PORT=7778
python app.py
```

### 4. 访问应用

在浏览器中打开: `https://localhost:7778`

## 常见问题

### Q: 提示"未找到Python"怎么办?

**A**: 请先安装Python:
- 访问 https://www.python.org/downloads/
- 下载并安装Python 3.8或更高版本
- 安装时勾选"Add Python to PATH"

### Q: 依赖安装失败怎么办?

**A**: 尝试手动安装:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

如果仍然失败,可能需要使用管理员权限:
- Windows: 以管理员身份运行命令提示符
- macOS/Linux: 使用 `sudo pip install -r requirements.txt`

### Q: SSL证书生成失败怎么办?

**A**: 有两种解决方案:

**方案1**: 安装OpenSSL
- Windows: `winget install OpenSSL.Light`
- macOS: `brew install openssl`
- Linux: `sudo apt-get install openssl`

**方案2**: 安装cryptography库
```bash
pip install cryptography
```

然后重新运行 `python generate_ssl_cert.py`

### Q: 端口7778已被占用怎么办?

**A**: 修改端口号:

1. 编辑 `deploy.bat` 或 `deploy.py`
2. 将 `HTTPS_PORT=7778` 改为其他端口,如 `HTTPS_PORT=8443`
3. 重新运行部署脚本

### Q: 浏览器没有自动打开怎么办?

**A**: 手动在浏览器中访问:
```
https://localhost:7778
```

### Q: 如何使用HTTP而不是HTTPS?

**A**: 直接运行:
```bash
python app.py
```

应用会在 `http://localhost:7777` 启动。

> **注意**: 某些功能(如地理位置)可能需要HTTPS才能正常工作。

## 故障排除

### 检查服务器状态

如果应用无法访问,检查终端输出:

✅ **正常启动**:
```
启动HTTPS服务器...
访问地址: https://localhost:7778
 * Running on https://0.0.0.0:7778
```

❌ **端口被占用**:
```
OSError: [Errno 48] Address already in use
```
解决方法: 更改端口或关闭占用端口的程序

❌ **证书文件不存在**:
```
错误: SSL证书文件不存在!
```
解决方法: 运行 `python generate_ssl_cert.py`

### 查看日志

应用日志会显示在终端中,包括:
- 数据库初始化状态
- HTTP请求记录
- 错误信息

### 重置数据库

如果需要重置数据库:

1. 停止服务器 (Ctrl+C)
2. 删除 `data/punch_timer.db` 文件
3. 重新启动服务器

## 开发模式

### 启用调试模式

应用默认在调试模式下运行,提供:
- 代码自动重载
- 详细错误信息
- 调试工具栏

### 修改代码

修改代码后,服务器会自动重启。无需手动重启。

## 生产环境部署

本地部署脚本仅用于开发和测试。

生产环境部署请参考:
- [Zeabur部署指南](ZEABUR_DEPLOYMENT.md)
- [Render部署指南](RENDER_DEPLOYMENT.md)
- [云部署指南](CLOUD_DEPLOYMENT_GUIDE.md)

## 技术支持

如果遇到问题:

1. 查看本文档的"常见问题"和"故障排除"部分
2. 检查终端输出的错误信息
3. 查看项目的其他文档文件

## 文件说明

- `deploy.bat` - Windows一键部署脚本
- `deploy.py` - 跨平台Python部署脚本
- `generate_ssl_cert.py` - SSL证书生成脚本
- `app.py` - Flask应用主文件
- `requirements.txt` - Python依赖列表
- `ssl/` - SSL证书目录
- `data/` - SQLite数据库目录
- `templates/` - HTML模板目录
- `static/` - 静态资源目录

## 下一步

部署成功后:

1. 在浏览器中访问 `https://localhost:7778`
2. 点击"注册"创建账户
3. 登录后即可开始使用打卡功能

祝您使用愉快! 🎉
