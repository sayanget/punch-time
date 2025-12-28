# 打卡计时器 - 数据库部署指南

本指南将帮助你配置免费的PostgreSQL数据库,解决Render等云平台的数据持久化问题。

## 📋 目录

1. [为什么需要数据库](#为什么需要数据库)
2. [推荐方案: Supabase](#推荐方案-supabase)
3. [其他免费数据库选项](#其他免费数据库选项)
4. [本地开发配置](#本地开发配置)
5. [数据迁移](#数据迁移)
6. [常见问题](#常见问题)

---

## 为什么需要数据库

在Render、Heroku等云平台部署时,使用JSON文件存储数据会遇到以下问题:

- ❌ **服务重启后数据丢失** - 容器文件系统是临时的
- ❌ **每次部署都需要重新注册** - 用户账号无法保存
- ❌ **打卡记录无法持久化** - 所有历史记录会被清空

使用数据库可以解决这些问题:

- ✅ **数据永久保存** - 独立于应用容器
- ✅ **支持更多用户** - 更好的并发性能
- ✅ **完全免费** - 使用免费数据库服务

---

## 推荐方案: Supabase

**Supabase** 是最推荐的免费PostgreSQL数据库服务。

### 优势

- ✅ **永久免费** - 500MB存储空间
- ✅ **无需信用卡** - 注册即可使用
- ✅ **自动备份** - 数据安全有保障
- ✅ **全球CDN** - 访问速度快

### 配置步骤

#### 1. 注册Supabase账号

访问 [https://supabase.com](https://supabase.com) 并注册账号(可使用GitHub登录)

#### 2. 创建新项目

1. 点击 **"New Project"**
2. 填写项目信息:
   - **Name**: `punch-timer` (或任意名称)
   - **Database Password**: 设置一个强密码(请记住!)
   - **Region**: 选择离你最近的区域(如 `Northeast Asia (Tokyo)`)
3. 点击 **"Create new project"**
4. 等待1-2分钟项目创建完成

#### 3. 获取数据库连接字符串

1. 在项目页面,点击左侧菜单的 **"Project Settings"** (齿轮图标)
2. 点击 **"Database"** 标签
3. 找到 **"Connection string"** 部分
4. 选择 **"URI"** 模式
5. 复制连接字符串,格式类似:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
   ```
6. 将 `[YOUR-PASSWORD]` 替换为你在步骤2中设置的密码

#### 4. 初始化数据库表

1. 在Supabase项目页面,点击左侧菜单的 **"SQL Editor"**
2. 点击 **"New query"**
3. 复制以下SQL代码并执行:

```sql
-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建打卡记录表
CREATE TABLE IF NOT EXISTS punches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    punch_date DATE NOT NULL,
    punch_time TIMESTAMP NOT NULL,
    is_late_shift BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, punch_time),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_punches_user_date ON punches(user_id, punch_date);
```

4. 点击 **"Run"** 执行SQL
5. 确认显示 **"Success. No rows returned"**

#### 5. 配置Render环境变量

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 选择你的Web Service
3. 点击 **"Environment"** 标签
4. 添加环境变量:
   - **Key**: `DATABASE_URL`
   - **Value**: 粘贴步骤3中获取的连接字符串
5. 点击 **"Save Changes"**
6. Render会自动重新部署应用

#### 6. 验证部署

1. 等待Render部署完成
2. 访问你的应用URL
3. 注册一个新账号
4. 在Render Dashboard中点击 **"Manual Deploy"** → **"Clear build cache & deploy"** 重新部署
5. 重新访问应用,使用刚才注册的账号登录
6. 如果能成功登录,说明数据库配置成功! 🎉

---

## 其他免费数据库选项

### ElephantSQL

- **免费额度**: 20MB存储
- **注册**: [https://www.elephantsql.com](https://www.elephantsql.com)
- **优点**: 简单易用,无需信用卡
- **缺点**: 存储空间较小

**配置步骤**:
1. 注册并创建新实例(选择 **Tiny Turtle** 免费套餐)
2. 复制 **URL** 连接字符串
3. 在Render中设置 `DATABASE_URL` 环境变量

### Render PostgreSQL

- **免费额度**: 90天后过期
- **注册**: 在Render Dashboard中创建
- **优点**: 与Web Service在同一平台
- **缺点**: 90天后需要付费或迁移

**配置步骤**:
1. 在Render Dashboard点击 **"New +"** → **"PostgreSQL"**
2. 选择 **Free** 套餐
3. 创建后复制 **Internal Database URL**
4. 在Web Service中设置 `DATABASE_URL` 环境变量

### Railway PostgreSQL

- **免费额度**: $5/月额度
- **注册**: [https://railway.app](https://railway.app)
- **优点**: 慷慨的免费额度
- **缺点**: 需要验证GitHub账号

---

## 本地开发配置

### 使用SQLite(推荐)

无需安装PostgreSQL,应用会自动使用SQLite:

```bash
# 不设置DATABASE_URL环境变量,或设置为:
DATABASE_URL=sqlite:///punch_timer.db
```

### 使用本地PostgreSQL

如果你想在本地使用PostgreSQL:

1. 安装PostgreSQL
2. 创建数据库:
   ```bash
   createdb punch_timer
   ```
3. 设置环境变量:
   ```bash
   DATABASE_URL=postgresql://localhost/punch_timer
   ```

---

## 数据迁移

如果你已经有JSON文件中的数据,可以迁移到数据库:

### 迁移步骤

1. 确保 `users.json` 和 `punches.json` 文件存在
2. 配置好 `DATABASE_URL` 环境变量
3. 运行迁移脚本:
   ```bash
   python migrate_to_db.py
   ```
4. 查看迁移日志,确认数据已成功导入
5. 备份原JSON文件:
   ```bash
   mkdir backup
   move users.json backup/
   move punches.json backup/
   ```

### 迁移脚本说明

`migrate_to_db.py` 会:
- 读取 `users.json` 中的所有用户
- 读取 `punches.json` 中的所有打卡记录
- 将数据导入到PostgreSQL数据库
- 自动处理重复数据(跳过已存在的记录)

---

## 常见问题

### Q1: 如何查看数据库中的数据?

**Supabase**:
1. 在项目页面点击 **"Table Editor"**
2. 选择 `users` 或 `punches` 表查看数据

**其他数据库**:
使用数据库客户端工具如 [DBeaver](https://dbeaver.io/) 或 [pgAdmin](https://www.pgadmin.org/)

### Q2: 数据库连接失败怎么办?

检查以下几点:
1. `DATABASE_URL` 格式是否正确
2. 数据库密码是否包含特殊字符(需要URL编码)
3. 网络是否可以访问数据库服务器
4. 查看应用日志获取详细错误信息

### Q3: 如何备份数据库?

**Supabase**:
- 自动每日备份(免费套餐保留7天)
- 手动备份: SQL Editor → 导出数据

**手动备份**:
```bash
# 导出数据
pg_dump $DATABASE_URL > backup.sql

# 恢复数据
psql $DATABASE_URL < backup.sql
```

### Q4: 免费额度用完了怎么办?

- **Supabase**: 500MB对于打卡应用来说非常充足,几乎不可能用完
- **ElephantSQL**: 如果20MB不够,可以升级或迁移到Supabase
- **Render PostgreSQL**: 90天后迁移到Supabase

### Q5: 如何切换数据库?

1. 在新数据库中执行表创建SQL
2. 更新 `DATABASE_URL` 环境变量
3. 运行迁移脚本导入数据(如果需要)
4. 重新部署应用

### Q6: 本地开发和生产环境使用不同数据库?

可以!应用会根据 `DATABASE_URL` 自动选择:
- 本地: `DATABASE_URL=sqlite:///punch_timer.db`
- 生产: `DATABASE_URL=postgresql://...` (在Render中设置)

---

## 下一步

1. ✅ 选择数据库服务(推荐Supabase)
2. ✅ 按照上述步骤配置数据库
3. ✅ 在Render中设置环境变量
4. ✅ 部署并测试应用
5. ✅ (可选)迁移现有JSON数据

**需要帮助?** 查看 [Supabase文档](https://supabase.com/docs) 或 [Render文档](https://render.com/docs)
