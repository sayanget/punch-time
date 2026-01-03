# Northflank 部署指南

本指南将帮助你将打卡计时器应用部署到 Northflank 平台。

## 🌟 为什么选择 Northflank

- ✅ **完全免费,24/7运行,不休眠**
- ✅ 支持Docker容器化部署
- ✅ 自动Git部署
- ✅ 内置PostgreSQL数据库
- ✅ 简单易用的Web界面

---

## 📋 部署前准备

### 1. 注册Northflank账户

1. 访问 [https://northflank.com](https://northflank.com)
2. 点击 "Sign Up" 注册免费账户
3. 使用GitHub账户登录(推荐)

### 2. 准备GitHub仓库

确保你的代码已推送到GitHub仓库,包含以下文件:
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ `app.py`
- ✅ `db_config.py`
- ✅ `db_models.py`
- ✅ `templates/` 目录
- ✅ `static/` 目录

---

## 🚀 部署步骤

### 步骤1: 创建项目

1. 登录Northflank控制台
2. 点击 **"Create Project"**
3. 输入项目名称: `punch-timer`
4. 点击 **"Create Project"**

### 步骤2: 创建PostgreSQL数据库

1. 在项目中,点击 **"Add Service"** → **"Database"**
2. 选择 **"PostgreSQL"**
3. 配置数据库:
   - **Name**: `punch-timer-db`
   - **Version**: `15` (或最新版本)
   - **Plan**: 选择 **Free** 套餐
4. 点击 **"Create Database"**
5. 等待数据库创建完成(约1-2分钟)
6. 创建完成后,记下数据库连接信息:
   - 点击数据库服务
   - 找到 **"Connection Details"**
   - 复制 **"Internal Connection String"** (格式: `postgresql://...`)

### 步骤3: 部署应用

1. 在项目中,点击 **"Add Service"** → **"Combined Service"**
2. 选择 **"Git Repository"**
3. 连接GitHub:
   - 点击 **"Connect GitHub"**
   - 授权Northflank访问你的仓库
   - 选择 `punch-timer` 仓库
   - 分支选择: `main` 或 `master`
4. 配置服务:
   - **Name**: `punch-timer-app`
   - **Build Type**: 选择 **"Dockerfile"**
   - **Dockerfile Path**: `Dockerfile` (默认)
   - **Port**: `7777`

### 步骤4: 配置环境变量

在 **"Environment Variables"** 部分添加以下变量:

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SECRET_KEY` | `your-random-secret-key-here` | Flask密钥(随机字符串) |
| `DATABASE_URL` | `postgresql://...` | 从步骤2复制的数据库连接字符串 |
| `PORT` | `7777` | 应用端口 |
| `FLASK_DEBUG` | `False` | 生产环境关闭调试 |

> **重要**: `SECRET_KEY` 请使用随机字符串,可以用以下命令生成:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 步骤5: 配置健康检查(可选但推荐)

在 **"Health Checks"** 部分:
- **Path**: `/`
- **Port**: `7777`
- **Initial Delay**: `30` 秒
- **Timeout**: `10` 秒

### 步骤6: 部署

1. 检查所有配置无误
2. 点击 **"Create Service"**
3. Northflank将自动:
   - 克隆你的GitHub仓库
   - 构建Docker镜像
   - 部署应用
   - 初始化数据库

### 步骤7: 查看部署状态

1. 在服务列表中找到 `punch-timer-app`
2. 查看 **"Logs"** 标签,确认应用启动成功
3. 等待状态变为 **"Running"** (绿色)

### 步骤8: 获取访问URL

1. 点击服务名称
2. 在 **"Networking"** 标签下找到 **"Public URL"**
3. 复制URL,格式类似: `https://punch-timer-app-xxxxx.northflank.app`
4. 在浏览器中访问该URL

---

## 🔧 数据库初始化

应用首次启动时会自动创建数据库表结构,无需手动操作。

如果需要手动初始化或迁移数据:

1. 在Northflank控制台,进入 `punch-timer-app` 服务
2. 点击 **"Terminal"** 标签
3. 运行以下命令:
```bash
python -c "from db_config import init_database; init_database()"
```

---

## 📊 监控和日志

### 查看日志
1. 进入服务详情页
2. 点击 **"Logs"** 标签
3. 实时查看应用日志

### 监控资源使用
1. 点击 **"Metrics"** 标签
2. 查看CPU、内存、网络使用情况

---

## 🔄 自动部署

Northflank支持Git自动部署:

1. 在服务设置中,找到 **"Build Settings"**
2. 启用 **"Auto-deploy on push"**
3. 每次推送代码到GitHub,Northflank会自动重新部署

---

## 🛠️ 常见问题

### 1. 应用无法启动

**检查日志**:
- 查看 **"Logs"** 标签
- 确认数据库连接字符串正确
- 确认所有环境变量已设置

**常见错误**:
```
Error: could not connect to database
```
**解决**: 检查 `DATABASE_URL` 是否正确,确保使用 **Internal Connection String**

### 2. 数据库连接失败

**解决方案**:
1. 确认数据库服务状态为 **"Running"**
2. 使用数据库的 **Internal Connection String** (不是External)
3. 确保连接字符串格式为: `postgresql://user:password@host:port/database`

### 3. 端口配置错误

**解决方案**:
- 确保Dockerfile中 `EXPOSE 7777`
- 确保环境变量 `PORT=7777`
- 确保服务配置中端口为 `7777`

### 4. 构建失败

**检查**:
- 确认 `Dockerfile` 语法正确
- 确认 `requirements.txt` 中所有依赖都可用
- 查看构建日志找到具体错误

---

## 🔐 安全建议

1. **SECRET_KEY**: 使用强随机字符串,不要使用默认值
2. **数据库密码**: Northflank自动生成,无需修改
3. **环境变量**: 敏感信息存储在环境变量中,不要硬编码

---

## 💰 费用说明

Northflank免费套餐包括:
- ✅ 1个免费项目
- ✅ 2个免费服务(应用+数据库)
- ✅ 24/7运行,不休眠
- ✅ 自动SSL证书
- ✅ 基础监控和日志

**完全免费,无需信用卡!**

---

## 📚 更多资源

- [Northflank官方文档](https://northflank.com/docs)
- [PostgreSQL连接指南](https://northflank.com/docs/databases/postgresql)
- [Docker部署指南](https://northflank.com/docs/deployments/docker)

---

## 🎉 部署完成!

现在你的打卡计时器应用已经成功部署到Northflank,享受24/7不间断服务!

**下一步**:
- 📱 分享URL给团队成员
- 🔔 设置监控告警(可选)
- 🚀 配置自定义域名(可选)

---

## 🆚 与Render对比

| 特性 | Northflank | Render |
|------|------------|--------|
| 免费套餐 | ✅ 永久免费 | ✅ 永久免费 |
| 休眠机制 | ❌ 不休眠 | ⚠️ 15分钟后休眠 |
| 冷启动时间 | ⚡ 即时 | 🐌 15-50秒 |
| 数据库 | ✅ 免费PostgreSQL | ⚠️ 需付费 |
| 自动部署 | ✅ 支持 | ✅ 支持 |
| 容器支持 | ✅ 原生Docker | ✅ 支持 |

**结论**: Northflank在免费套餐上优于Render,特别是无休眠机制!
