# 部署故障排查速查卡

## 🚨 502错误快速诊断 (3分钟)

### 步骤1: 查看Runtime Logs (30秒)
```bash
# 找到这一行:
Listening at: http://X.X.X.X:YYYY
```

### 步骤2: 检查三要素 (1分钟)

| 检查项 | 正确值 | 错误值 |
|--------|--------|--------|
| **地址** | `0.0.0.0` | `127.0.0.1` |
| **端口** | 与Networking一致 | 不一致 |
| **协议** | `http://` | `https://` |

### 步骤3: 修复配置 (1.5分钟)

#### 问题A: 地址错误
```python
# 修改代码
app.run(host='0.0.0.0', port=8080)
```

#### 问题B: 端口不匹配
```
Networking → Container Port → 改为应用端口
```

#### 问题C: 协议错误
```python
# 移除SSL配置
app.run(host='0.0.0.0', port=8080)
# 不要: ssl_context=(...)
```

---

## 📋 常见错误速查表

| 错误信息 | 5秒诊断 | 10秒解决 |
|---------|---------|---------|
| **502** | 端口不匹配 | 改Networking配置 |
| **Address in use** | 端口占用 | 改端口或杀进程 |
| **SSL Error** | 容器内用了HTTPS | 改用HTTP |
| **ModuleNotFoundError** | 依赖未装 | `pip install -r requirements.txt` |
| **Connection refused** | 数据库连接失败 | 检查DATABASE_URL |

---

## 🎯 一分钟检查清单

### 云端部署 (Zeabur/Render/Railway)
```
□ Logs显示: http://0.0.0.0:XXXX
□ 端口 = Networking配置
□ 无SSL配置
□ 环境变量无${自引用}
```

### 本地开发
```
□ Python >= 3.8
□ pip install完成
□ SSL证书存在 (如需HTTPS)
□ 端口未占用
```

---

## 💡 黄金法则

### 法则1: 90%的502是端口问题
```
应用端口 ≠ Networking端口 → 502
```

### 法则2: 容器内永远用HTTP
```
容器: HTTP → 边缘代理: HTTPS → 用户
```

### 法则3: 必须监听0.0.0.0
```
127.0.0.1 = 只能本地访问 → 502
0.0.0.0 = 接受外部访问 → ✅
```

---

## 🔧 一键修复命令

### 检查端口占用
```bash
# Windows
netstat -ano | findstr :8080

# Linux/Mac
lsof -i :8080
```

### 生成SSL证书
```bash
# Python方式
pip install cryptography
python generate_ssl_cert.py

# OpenSSL方式
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"
```

### 验证依赖
```bash
pip list | grep -i flask
pip list | grep -i gunicorn
```

---

## 📞 紧急救援流程

### 情况1: 生产环境502,用户无法访问

```
1. [10秒] 查看服务状态
   → Running? 继续
   → Stopped? 查看Build Logs

2. [20秒] 查看Runtime Logs最后10行
   → 找到 "Listening at: http://X:YYYY"

3. [30秒] 打开Networking配置
   → Container Port = YYYY?
   → 不等于? 立即修改为YYYY

4. [60秒] 等待服务重启
   → 验证访问恢复
```

**预计恢复时间: 2分钟**

### 情况2: 本地无法启动

```
1. [5秒] 看错误信息
   → SSL证书? 运行 generate_ssl_cert.py
   → 端口占用? 改端口或杀进程
   → 依赖缺失? pip install -r requirements.txt

2. [30秒] 执行修复

3. [5秒] 重新启动
```

**预计恢复时间: 1分钟**

---

## 🎓 记忆口诀

```
云端部署三要素:
地址零零零零 (0.0.0.0)
端口要一致
协议用HTTP

本地开发三检查:
Python版本够
依赖全装好
证书要生成
```

---

## 📱 移动端快速参考

### 502错误
```
1. Logs → Listening at
2. 端口 = Networking?
3. 不等于 → 改配置
```

### 启动失败
```
1. 看错误
2. SSL? → 生成证书
3. 端口? → 改端口
4. 依赖? → pip install
```

---

## 🔗 相关资源

- [完整技能文档](SKILL.md)
- [案例研究](examples/case-studies.md)
- [README](README.md)

---

**最后更新**: 2026-01-19  
**版本**: 1.0  
**适用平台**: Zeabur, Render, Railway, Heroku
