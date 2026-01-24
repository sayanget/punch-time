# Flask应用部署故障排查技能

这是一个系统化的Flask应用部署故障排查技能,帮助快速诊断和解决本地开发环境和云端PaaS平台的部署问题。

## 技能概述

- **名称**: deployment-troubleshooting
- **类型**: 诊断和故障排查
- **适用平台**: Zeabur, Render, Railway, Heroku等PaaS平台
- **适用框架**: Flask, Django, FastAPI等Python Web框架

## 主要功能

1. **本地环境诊断**
   - Python环境检查
   - SSL证书问题排查
   - 端口占用检测
   - 依赖包验证

2. **云端部署诊断**
   - 502/503错误系统性排查
   - 监听地址配置检查
   - 端口配置匹配验证
   - HTTP/HTTPS协议诊断
   - 环境变量配置审查

3. **日志分析**
   - 关键日志模式识别
   - 错误信息解读
   - 日志提取技巧

## 快速开始

### 使用场景1: Zeabur部署502错误

```bash
# 1. 查看Runtime Logs
# 找到: Listening at: http://0.0.0.0:8080

# 2. 检查Networking配置
# Container Port: 7778 (不匹配!)

# 3. 修复
# 将Container Port改为8080

# 4. 验证
# 访问应用URL,确认正常
```

### 使用场景2: 本地HTTPS启动失败

```bash
# 1. 生成SSL证书
python generate_ssl_cert.py

# 2. 验证证书文件
ls ssl/cert.pem ssl/key.pem

# 3. 启动应用
python app.py
```

## 核心检查清单

### 云端部署必查项
- [ ] 监听地址是 `0.0.0.0` 而非 `127.0.0.1`
- [ ] 应用端口与Networking配置一致
- [ ] 容器内使用HTTP,不使用HTTPS
- [ ] 环境变量无自引用(如`PORT=${PORT}`)
- [ ] Runtime Logs无错误信息

### 本地部署必查项
- [ ] Python版本 >= 3.8
- [ ] 依赖已安装
- [ ] SSL证书已生成(如需HTTPS)
- [ ] 端口未被占用

## 关键诊断命令

```bash
# 检查端口占用 (Windows)
netstat -ano | findstr :8080

# 检查端口占用 (Linux/Mac)
lsof -i :8080

# 查看Python版本
python --version

# 验证依赖安装
pip list | grep flask
```

## 常见问题速查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| 502 Service Unavailable | 端口不匹配 | 修改Networking配置 |
| Address already in use | 端口被占用 | 更改端口或终止进程 |
| SSL证书文件不存在 | 证书未生成 | 运行证书生成脚本 |
| ModuleNotFoundError | 依赖未安装 | pip install -r requirements.txt |
| Connection refused | 数据库连接失败 | 检查DATABASE_URL |

## 文件说明

- `SKILL.md` - 完整的技能文档和诊断流程
- `README.md` - 本文件,快速参考指南
- `examples/` - 实际案例和解决方案示例

## 最佳实践

1. **始终查看Runtime Logs** - 这是最直接的信息来源
2. **系统性排查** - 按照检查清单逐项验证
3. **理解架构差异** - 本地vs云端、HTTP vs HTTPS
4. **记录解决方案** - 为团队积累经验

## 贡献

欢迎提交实际遇到的部署问题和解决方案!

## 许可

MIT License
