# Google Maps API 设置指南

## 获取API密钥

### 步骤1：访问Google Cloud Console

1. 打开浏览器，访问 https://console.cloud.google.com/
2. 使用Google账号登录

### 步骤2：创建项目

1. 点击顶部导航栏的项目选择器
2. 点击"新建项目"
3. 输入项目名称（如："Punch Timer"）
4. 点击"创建"

### 步骤3：启用Geocoding API

1. 在左侧菜单中，选择"API和服务" → "库"
2. 搜索"Geocoding API"
3. 点击"Geocoding API"
4. 点击"启用"按钮

### 步骤4：创建API密钥

1. 在左侧菜单中，选择"API和服务" → "凭据"
2. 点击顶部的"+ 创建凭据"
3. 选择"API密钥"
4. 复制生成的API密钥

### 步骤5：（推荐）限制API密钥

为了安全，建议限制API密钥的使用范围：

1. 点击刚创建的API密钥旁边的编辑按钮
2. 在"应用限制"部分：
   - 选择"HTTP referrer（网站）"
   - 添加您的网站URL（如：`https://yourdomain.com/*`）
   - 本地开发添加：`https://localhost:7778/*`
3. 在"API限制"部分：
   - 选择"限制密钥"
   - 勾选"Geocoding API"
4. 点击"保存"

### 步骤6：配置应用

1. 在项目根目录创建`.env`文件（如果还没有）
2. 添加以下内容：

```bash
# Google Maps API密钥
GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

3. 将`AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`替换为您的实际API密钥

### 步骤7：重启应用

```bash
# 停止当前运行的服务器（Ctrl+C）

# 重新启动HTTPS服务器
$env:SSL_ENABLED='true'; $env:HTTPS_PORT='7778'; python app.py
```

---

## 验证配置

### 测试API密钥

1. 打开浏览器，访问 https://localhost:7778
2. 登录应用
3. 点击"记录打卡"按钮
4. 允许浏览器访问位置
5. 打开浏览器控制台（F12）
6. 查看控制台输出：
   - 如果看到"使用Google Maps地理编码: ..."，说明配置成功
   - 如果看到"使用Nominatim地理编码: ..."，说明Google Maps API未配置或失败

### 地址格式对比

**Google Maps（成功）：**
```
123 Main St, San Francisco, CA 94102
```

**Nominatim（降级）：**
```
Main Street, San Francisco, California, United States
```

---

## 费用说明

### 免费额度

- **每月免费额度**：$200信用额度
- **相当于**：约28,000次地理编码请求
- **超出后**：$5/1000次请求

### 使用估算

**小型应用（10用户）：**
```
10用户 × 4次打卡/天 × 20工作日 = 800次/月
成本：$0（完全在免费额度内）
```

**中型应用（100用户）：**
```
100用户 × 4次打卡/天 × 20工作日 = 8,000次/月
成本：$0（完全在免费额度内）
```

**大型应用（1000用户）：**
```
1000用户 × 4次打卡/天 × 20工作日 = 80,000次/月
超出额度：80,000 - 28,000 = 52,000次
成本：52,000 / 1000 × $5 = $260/月
```

### 成本控制

如果担心费用，可以设置配额限制：

1. 访问 https://console.cloud.google.com/
2. 选择"API和服务" → "配额"
3. 搜索"Geocoding API"
4. 设置每日请求限制（如：1000次/天）

---

## 降级机制

应用已实现三层降级机制：

1. **优先使用Google Maps**
   - 如果配置了API密钥
   - 地址格式：`123 Main St, San Francisco, CA 94102`

2. **降级到Nominatim**
   - 如果Google Maps失败或未配置
   - 地址格式：`Main Street, San Francisco, California`

3. **最终显示坐标**
   - 如果所有API都失败
   - 格式：`37.7749, -122.4194`

---

## 常见问题

### Q: API密钥无效？

**A:** 检查以下几点：
1. API密钥是否正确复制（没有多余空格）
2. Geocoding API是否已启用
3. API密钥限制是否正确配置
4. 是否重启了应用

### Q: 仍然显示Nominatim地址？

**A:** 可能原因：
1. `.env`文件未正确加载
2. API密钥未配置或为空
3. API密钥限制过于严格
4. 查看浏览器控制台的错误信息

### Q: 如何查看API使用量？

**A:** 
1. 访问 https://console.cloud.google.com/
2. 选择"API和服务" → "信息中心"
3. 查看"Geocoding API"的使用情况

### Q: 不想使用Google Maps怎么办？

**A:** 
不配置`GOOGLE_MAPS_API_KEY`即可，应用会自动使用免费的Nominatim API。

---

## 安全最佳实践

### 1. 不要提交API密钥到Git

确保`.env`文件在`.gitignore`中：

```bash
# .gitignore
.env
```

### 2. 使用环境变量

生产环境使用平台的环境变量功能：

**Render:**
1. 进入项目设置
2. 添加环境变量：`GOOGLE_MAPS_API_KEY`

**Heroku:**
```bash
heroku config:set GOOGLE_MAPS_API_KEY=your-api-key
```

### 3. 限制API密钥

- 限制HTTP referrer
- 限制API范围
- 设置配额限制

### 4. 定期轮换密钥

建议每6个月更换一次API密钥。

---

## 故障排除

### 问题：控制台显示"Google Maps API请求失败"

**解决方案：**
1. 检查网络连接
2. 验证API密钥是否有效
3. 确认Geocoding API已启用
4. 检查API密钥限制设置

### 问题：地址显示为坐标

**解决方案：**
1. 检查位置是否在美国（Google Maps在美国最准确）
2. 查看控制台错误信息
3. 验证API配额未超限

### 问题：应用无法启动

**解决方案：**
1. 检查`.env`文件格式是否正确
2. 确保没有语法错误
3. 查看终端错误信息

---

## 技术支持

如有问题，请查看：
- [Google Maps Geocoding API文档](https://developers.google.com/maps/documentation/geocoding)
- [Google Cloud Console](https://console.cloud.google.com/)
- [定价说明](https://developers.google.com/maps/documentation/geocoding/usage-and-billing)
