# Render部署指南 - 地理位置功能

## 🚀 快速部署步骤

### 1. Render会自动部署

GitHub推送后，Render会自动检测到更新并开始部署。

**查看部署状态：**
1. 访问 https://dashboard.render.com/
2. 找到您的 `punch-timer` 应用
3. 查看 "Events" 标签页
4. 等待部署完成（通常2-5分钟）

---

### 2. 配置环境变量

**必须添加Google Maps API密钥：**

1. 在Render Dashboard中，进入您的应用
2. 点击 "Environment" 标签页
3. 点击 "Add Environment Variable"
4. 添加以下变量：

```
Key: GOOGLE_MAPS_API_KEY
Value: 您的Google Maps API密钥
```

5. 点击 "Save Changes"

**注意：** 添加环境变量后，Render会自动重新部署应用。

---

### 3. 运行数据库迁移

部署完成后，需要运行数据库迁移以添加地理位置字段。

**方法A：使用Render Shell（推荐）**

1. 在Render Dashboard中，进入您的应用
2. 点击右上角的 "Shell" 按钮
3. 在Shell中运行：

```bash
python migrate_add_location.py
```

4. 输入 `yes` 确认迁移

**方法B：使用一次性任务**

如果Shell不可用，可以创建一次性任务：

1. 在应用页面，点击 "Manual Deploy"
2. 选择 "Clear build cache & deploy"
3. 部署完成后，在Shell中运行迁移脚本

---

### 4. 验证部署

**检查应用是否正常运行：**

1. 访问您的应用URL：`https://your-app-name.onrender.com`
2. 登录应用
3. 打开浏览器控制台（F12）
4. 点击打卡按钮
5. 允许位置权限
6. 检查控制台是否显示：
   ```
   使用Google Maps地理编码: [地址]
   ```

**检查HTTPS：**
- 浏览器地址栏应显示🔒图标
- URL应以 `https://` 开头
- 不应有SSL警告

**检查地理位置：**
- 打卡记录应显示地址（如：`123 Main St, City, State ZIP`）
- 不应只显示坐标

---

## 🔧 故障排除

### 问题1：部署失败

**检查：**
1. 查看Render的部署日志
2. 确认所有依赖都在 `requirements.txt` 中
3. 检查Python版本兼容性

**解决：**
- 查看错误信息
- 修复代码后重新推送到GitHub

### 问题2：地理位置不工作

**可能原因：**
1. 未配置 `GOOGLE_MAPS_API_KEY`
2. API密钥无效或受限
3. 未运行数据库迁移

**解决：**
1. 检查环境变量是否正确设置
2. 验证API密钥在Google Cloud Console中有效
3. 运行数据库迁移脚本

### 问题3：显示Nominatim地址而非Google Maps

**原因：** Google Maps API密钥未配置或无效

**解决：**
1. 检查Render环境变量中的 `GOOGLE_MAPS_API_KEY`
2. 确认API密钥没有多余空格
3. 验证Geocoding API已在Google Cloud Console中启用

### 问题4：数据库迁移失败

**可能原因：**
1. 数据库连接问题
2. 字段已存在

**解决：**
1. 检查 `DATABASE_URL` 环境变量
2. 如果字段已存在，迁移脚本会自动跳过

---

## 📋 完整环境变量列表

确保Render中配置了以下环境变量：

```bash
# 必需
DATABASE_URL=postgresql://...  # Render自动提供
SECRET_KEY=your-secret-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# 可选
FLASK_DEBUG=False
PYTHON_VERSION=3.11.0
```

---

## 🔍 验证清单

部署后检查以下项目：

- [ ] 应用可以通过HTTPS访问
- [ ] 可以正常登录
- [ ] 可以正常打卡
- [ ] 浏览器请求位置权限
- [ ] 打卡记录显示地址（而非坐标）
- [ ] 控制台显示 "使用Google Maps地理编码"
- [ ] 地址格式为：`Street, City, State ZIP`

---

## 📊 监控

### 查看应用日志

1. 在Render Dashboard中，进入您的应用
2. 点击 "Logs" 标签页
3. 查看实时日志

**关键日志：**
```
INFO:db_config:PostgreSQL数据库表初始化成功
INFO:werkzeug:127.0.0.1 - - [日期] "GET /api/config HTTP/1.1" 200
```

### 监控API使用量

定期检查Google Cloud Console中的API使用情况：
1. 访问 https://console.cloud.google.com/
2. 选择您的项目
3. 进入 "API和服务" → "信息中心"
4. 查看 "Geocoding API" 使用量

---

## 🎯 部署后测试脚本

您可以使用以下命令测试部署：

```bash
# 测试HTTPS
curl -I https://your-app-name.onrender.com

# 测试API配置端点（需要登录）
curl https://your-app-name.onrender.com/api/config

# 测试数据库连接
# 在Render Shell中运行
python -c "from db_config import engine; print(engine.url)"
```

---

## 📝 部署记录

**最新部署：**
- **日期：** 2026-01-18
- **提交：** 6707036
- **功能：** 添加地理位置追踪和Google Maps集成
- **状态：** ✅ 已推送到GitHub

**下一步：**
1. 等待Render自动部署
2. 添加 `GOOGLE_MAPS_API_KEY` 环境变量
3. 运行数据库迁移
4. 测试功能

---

## 🆘 需要帮助？

如果遇到问题：
1. 查看Render部署日志
2. 检查浏览器控制台错误
3. 验证环境变量配置
4. 确认数据库迁移已运行

**常见问题：**
- 地理位置需要HTTPS（Render自动提供）
- Google Maps API需要有效的密钥
- 数据库迁移必须在部署后运行
