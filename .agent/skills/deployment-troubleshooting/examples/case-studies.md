# 部署故障排查案例集

## 案例1: Zeabur部署502错误 - 端口不匹配

### 问题描述
- **平台**: Zeabur
- **症状**: 服务状态显示"Running",但访问返回502错误
- **URL**: https://punch-timer.zeabur.app
- **应用**: Flask + Gunicorn + PostgreSQL

### 诊断过程

#### 步骤1: 检查服务状态
```
服务状态: Running ✅
部署状态: 成功 ✅
```
服务正在运行,排除构建失败问题。

#### 步骤2: 查看Runtime Logs
```
[2026-01-20 00:24:54 +0000] [7] [INFO] Listening at: http://0.0.0.0:8080 (7)
[2026-01-20 00:24:54 +0000] [7] [INFO] Using worker: sync
[2026-01-20 00:24:54 +0000] [8] [INFO] Booting worker with pid: 8
INFO:db_config:PostgreSQL数据库表初始化成功
```

**关键发现**:
- ✅ 监听地址: `0.0.0.0` (正确)
- ✅ 协议: HTTP (正确)
- ✅ 数据库: 连接成功
- ⚠️ 监听端口: **8080**

#### 步骤3: 检查Networking配置
```
Networking → Ports
Container Port: 7778
```

**问题确认**: 应用监听8080,但Networking配置为7778 → 端口不匹配!

### 解决方案

1. 导航到Zeabur服务的"Networking"标签
2. 删除错误的端口配置(7778)
3. 添加正确的端口配置(8080)
4. 重新关联域名到8080端口
5. 等待服务重启

### 验证结果

访问 https://punch-timer.zeabur.app:
- ✅ 登录页面正常显示
- ✅ 无502错误
- ✅ HTTPS正常工作

### 经验总结

**根本原因**: 
- 应用监听端口与平台Networking配置不一致

**诊断要点**:
1. Runtime Logs是最直接的信息来源
2. 查找"Listening at"关键字确认端口
3. 对比应用端口和Networking配置

**预防措施**:
```python
# 使用环境变量,让平台自动设置端口
import os
port = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port)
```

---

## 案例2: 本地HTTPS启动失败 - SSL证书缺失

### 问题描述
- **环境**: Windows本地开发
- **症状**: 启动应用时报错
- **错误信息**: `错误: SSL证书文件不存在!`

### 诊断过程

#### 步骤1: 检查错误信息
```
错误: SSL证书文件不存在!
证书: ssl/cert.pem
密钥: ssl/key.pem
```

#### 步骤2: 验证文件存在性
```bash
ls ssl/
# 输出: 目录不存在或为空
```

**问题确认**: SSL证书文件未生成

### 解决方案

#### 方案1: 使用Python cryptography库
```python
# generate_ssl_cert.py
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
from pathlib import Path

# 创建ssl目录
ssl_dir = Path('ssl')
ssl_dir.mkdir(exist_ok=True)

# 生成私钥
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# 生成证书
subject = issuer = x509.Name([
    x509.NameAttribute(x509.NameOID.COMMON_NAME, u"localhost"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).sign(private_key, hashes.SHA256())

# 保存证书
with open('ssl/cert.pem', 'wb') as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

# 保存私钥
with open('ssl/key.pem', 'wb') as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

print("✓ SSL证书生成成功!")
```

#### 方案2: 使用OpenSSL命令行
```bash
# 生成私钥和自签名证书
openssl req -x509 -newkey rsa:4096 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -days 365 \
  -nodes \
  -subj "/CN=localhost"
```

### 验证结果

```bash
# 验证证书文件
ls ssl/
# 输出:
# cert.pem
# key.pem

# 启动应用
python app.py
# 输出:
# 启动HTTPS服务器...
# 访问地址: https://localhost:7778
# * Running on https://0.0.0.0:7778
```

### 经验总结

**根本原因**:
- 首次运行时未生成SSL证书

**最佳实践**:
1. 提供自动生成证书的脚本
2. 在启动脚本中检查证书是否存在
3. 提供清晰的错误提示和解决方案

**一键部署脚本示例**:
```batch
@echo off
REM 检查SSL证书
if not exist "ssl\cert.pem" (
    echo 正在生成SSL证书...
    python generate_ssl_cert.py
)

REM 启动应用
python app.py
```

---

## 案例3: 环境变量自引用问题

### 问题描述
- **平台**: Zeabur
- **症状**: 服务启动但端口配置异常
- **发现**: 环境变量中有 `PORT=${PORT}`

### 诊断过程

查看Variables配置:
```
PORT=${PORT}
DATABASE_URL=postgresql://...
SECRET_KEY=...
```

**问题**: `PORT=${PORT}` 是自引用,导致端口配置失效

### 解决方案

删除PORT环境变量,让Zeabur自动设置:
```
# 删除
PORT=${PORT}

# 保留
DATABASE_URL=postgresql://...
SECRET_KEY=...
```

### 经验总结

**常见环境变量问题**:
1. 自引用: `VAR=${VAR}`
2. 格式错误: `DATABASE_URL=postgres://...` (应为postgresql://)
3. 缺少必需变量: SECRET_KEY未设置

**最佳实践**:
- 不要手动设置PORT,让平台自动注入
- 使用.env.example作为模板
- 验证环境变量格式

---

## 案例4: 监听地址127.0.0.1导致502

### 问题描述
- **平台**: Railway
- **症状**: 本地运行正常,部署后502
- **应用**: Flask应用

### 诊断过程

#### 本地代码
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
```

#### Runtime Logs
```
* Running on http://127.0.0.1:5000
```

**问题**: 只监听本地回环地址,无法接收外部请求

### 解决方案

修改监听地址为0.0.0.0:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
```

### 验证结果

```
* Running on http://0.0.0.0:5000
```

访问应用URL,成功加载。

### 经验总结

**关键概念**:
- `127.0.0.1`: 只接受本地连接
- `0.0.0.0`: 接受所有网络接口的连接

**容器化环境必须使用0.0.0.0**

---

## 通用诊断模板

```markdown
## 案例X: [问题简述]

### 问题描述
- **平台**: 
- **症状**: 
- **错误信息**: 

### 诊断过程
1. 检查服务状态
2. 查看Runtime Logs
3. 验证配置
4. 确认问题

### 解决方案
[具体步骤]

### 验证结果
[验证方法和结果]

### 经验总结
- **根本原因**: 
- **预防措施**: 
- **最佳实践**: 
```

## 贡献案例

欢迎提交您遇到的部署问题和解决方案!请按照上述模板格式编写。
