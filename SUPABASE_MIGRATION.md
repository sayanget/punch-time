# Supabase数据库迁移指南

## 📋 迁移内容

为 `punches` 表添加地理位置字段：
- `latitude` - 纬度（DOUBLE PRECISION）
- `longitude` - 经度（DOUBLE PRECISION）
- `location_name` - 地点名称（VARCHAR(500)）

---

## 🚀 执行迁移（3种方法）

### 方法1：Supabase SQL Editor（推荐）

1. **登录Supabase**
   - 访问 https://supabase.com/dashboard
   - 选择您的项目

2. **打开SQL Editor**
   - 左侧菜单选择 "SQL Editor"
   - 点击 "New query"

3. **复制并执行SQL**
   - 打开 `supabase_migration_add_location.sql`
   - 复制全部内容
   - 粘贴到SQL Editor
   - 点击 "Run" 或按 `Ctrl + Enter`

4. **验证结果**
   - 应该看到成功消息
   - 检查 "Results" 标签页确认字段已添加

---

### 方法2：使用Supabase CLI

```bash
# 1. 安装Supabase CLI（如果还没有）
npm install -g supabase

# 2. 登录
supabase login

# 3. 链接到您的项目
supabase link --project-ref your-project-ref

# 4. 执行迁移
supabase db push --file supabase_migration_add_location.sql
```

---

### 方法3：使用Python脚本（已部署到Render）

如果您的应用已部署到Render并连接到Supabase：

1. 在Render Dashboard中打开Shell
2. 运行迁移脚本：
```bash
python migrate_add_location.py
```
3. 输入 `yes` 确认

---

## ✅ 验证迁移

### 在Supabase Dashboard中验证

1. 进入 "Table Editor"
2. 选择 `punches` 表
3. 检查是否有以下新列：
   - `latitude`
   - `longitude`
   - `location_name`

### 使用SQL查询验证

```sql
-- 查看表结构
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'punches'
ORDER BY ordinal_position;

-- 查看新字段
SELECT 
    column_name, 
    data_type
FROM information_schema.columns
WHERE table_name = 'punches' 
    AND column_name IN ('latitude', 'longitude', 'location_name');
```

---

## 🔄 回滚迁移（如果需要）

如果需要撤销迁移，在SQL Editor中执行：

```sql
-- 删除地理位置字段
ALTER TABLE punches DROP COLUMN IF EXISTS latitude;
ALTER TABLE punches DROP COLUMN IF EXISTS longitude;
ALTER TABLE punches DROP COLUMN IF EXISTS location_name;
```

---

## 📊 Supabase免费版限制

**您的免费版配额：**
- ✅ 数据库大小：500 MB
- ✅ 带宽：2 GB/月
- ✅ API请求：无限制
- ✅ 存储：1 GB

**新增字段的影响：**
- 每条打卡记录增加约50-100字节
- 1000条记录 ≈ 0.1 MB
- 对免费版配额影响极小

---

## 🔍 常见问题

### Q: 迁移会影响现有数据吗？

**A:** 不会。新字段会被添加，现有记录的这些字段值为 `NULL`。

### Q: 迁移需要多长时间？

**A:** 通常几秒钟即可完成，取决于表中的记录数量。

### Q: 如果字段已存在会怎样？

**A:** SQL脚本会检查字段是否存在，如果已存在则跳过，不会报错。

### Q: 需要停机吗？

**A:** 不需要。迁移可以在应用运行时执行。

### Q: 免费版有迁移次数限制吗？

**A:** 没有。您可以随时执行SQL语句。

---

## 📝 迁移记录

**迁移文件：** `supabase_migration_add_location.sql`  
**创建日期：** 2026-01-18  
**功能：** 添加地理位置追踪字段  
**影响：** 添加3个新字段到 `punches` 表  
**数据影响：** 无（仅添加字段）  

---

## 🎯 下一步

迁移完成后：

1. ✅ 在Render中添加 `GOOGLE_MAPS_API_KEY` 环境变量
2. ✅ 重新部署应用（如果需要）
3. ✅ 测试打卡功能
4. ✅ 验证地理位置显示

---

## 💡 提示

- 建议在执行迁移前备份数据库（虽然此迁移是安全的）
- 可以在Supabase Dashboard的 "Database" → "Backups" 中创建备份
- 免费版支持每日自动备份（保留7天）

---

## 🆘 需要帮助？

如果遇到问题：
1. 检查SQL语法错误
2. 确认您有数据库修改权限
3. 查看Supabase Dashboard的错误消息
4. 检查表名是否正确（应为 `punches`）
