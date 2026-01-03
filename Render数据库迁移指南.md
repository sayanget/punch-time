# Render数据库迁移操作指南

## 问题说明
由于数据库的唯一约束 `UNIQUE(user_id, punch_time)`,导致相同的`punch_time`无法在不同的`punch_date`中存在,从而使末班打卡无法复制到前一天。

## 解决方案
需要修改数据库唯一约束,从 `UNIQUE(user_id, punch_time)` 改为 `UNIQUE(user_id, punch_date, punch_time)`。

## 操作步骤

### 方法1: 使用Render Shell(推荐)

#### 步骤1: 访问Render控制台
1. 打开浏览器访问: https://dashboard.render.com
2. 登录您的账号
3. 找到 `punch-time` 服务

#### 步骤2: 打开Shell
1. 在服务详情页,点击顶部的"Shell"标签
2. 等待Shell连接成功

#### 步骤3: 连接到PostgreSQL数据库
在Shell中输入以下命令:
```bash
# 使用环境变量中的DATABASE_URL连接
psql $DATABASE_URL
```

#### 步骤4: 查看当前约束
```sql
-- 查看punches表的所有约束
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'punches'::regclass;
```

**预期输出**:
```
           conname            | contype 
------------------------------+---------
 punches_pkey                 | p
 punches_user_id_punch_time_key | u
 punches_user_id_fkey         | f
```

#### 步骤5: 执行迁移SQL
```sql
-- 删除旧的唯一约束
ALTER TABLE punches DROP CONSTRAINT IF EXISTS punches_user_id_punch_time_key;

-- 添加新的唯一约束
ALTER TABLE punches ADD CONSTRAINT punches_user_id_punch_date_punch_time_key 
    UNIQUE (user_id, punch_date, punch_time);
```

**预期输出**:
```
ALTER TABLE
ALTER TABLE
```

#### 步骤6: 验证新约束
```sql
-- 再次查看约束
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'punches'::regclass;
```

**预期输出**:
```
                conname                 | contype 
----------------------------------------+---------
 punches_pkey                           | p
 punches_user_id_punch_date_punch_time_key | u
 punches_user_id_fkey                   | f
```

#### 步骤7: 退出PostgreSQL
```sql
\q
```

#### 步骤8: 退出Shell
```bash
exit
```

### 方法2: 使用本地psql连接(如果有数据库URL)

如果您有Render PostgreSQL的连接URL:

```bash
# 从Render控制台获取DATABASE_URL
# 格式: postgresql://user:password@host:port/database

# 本地连接
psql "postgresql://user:password@host:port/database"

# 然后执行步骤4-7的SQL命令
```

### 方法3: 使用数据库管理工具

可以使用以下工具连接到Render PostgreSQL:
- pgAdmin
- DBeaver
- TablePlus
- DataGrip

连接后,执行迁移SQL脚本。

## 迁移后验证

### 1. 检查Render部署状态
1. 确认Render已自动部署最新代码
2. 查看部署日志,确认没有错误

### 2. 测试末班打卡功能

#### 测试步骤:
1. 访问 https://punch-time.onrender.com
2. 登录您的账号
3. **测试手动末班打卡**:
   - 选择日期: 2026-01-04
   - 添加正常打卡: 08:30, 12:00, 13:30
   - 添加一个下午的打卡: 18:00
   - **勾选"末班打卡"选项**
   - 点击打卡
4. **验证结果**:
   - 查看 2026-01-03,应该看到这条打卡记录(作为最后一条)
   - 查看 2026-01-04,也应该看到这条打卡记录

#### 测试自动末班打卡:
1. 选择日期: 2026-01-05
2. 添加凌晨打卡: 03:30
3. 验证:
   - 2026-01-04 应该有这条记录
   - 2026-01-05 也应该有这条记录

### 3. 测试删除功能
1. 删除一条末班打卡记录
2. 验证两个日期的记录都被删除

### 4. 测试导出功能
1. 点击"导出数据"
2. 检查CSV文件,确认末班打卡只在前一天显示一次

## 常见问题

### Q1: 如果找不到Shell标签怎么办?
**A**: Shell功能可能需要付费计划。可以使用方法2或方法3,或者联系Render支持。

### Q2: 如果约束名称不同怎么办?
**A**: 使用步骤4的SQL查询实际的约束名称,然后在步骤5中使用正确的名称。

### Q3: 如果迁移失败怎么办?
**A**: 
1. 检查错误信息
2. 确认数据库连接正常
3. 确认有足够的权限
4. 如果有现有数据冲突,可能需要先清理数据

### Q4: 迁移会影响现有数据吗?
**A**: 
- 不会删除或修改现有数据
- 只是修改约束规则
- 但如果现有数据违反新约束,迁移会失败
- 建议先备份数据库

### Q5: 如何备份数据库?
**A**: 在Render控制台:
1. 进入PostgreSQL数据库服务
2. 点击"Backups"
3. 点击"Create Backup"

## 回滚方案

如果迁移后出现问题,可以回滚:

```sql
-- 删除新约束
ALTER TABLE punches DROP CONSTRAINT IF EXISTS punches_user_id_punch_date_punch_time_key;

-- 恢复旧约束
ALTER TABLE punches ADD CONSTRAINT punches_user_id_punch_time_key 
    UNIQUE (user_id, punch_time);
```

## 完成检查清单

- [ ] 已连接到Render PostgreSQL数据库
- [ ] 已查看当前约束
- [ ] 已执行迁移SQL
- [ ] 已验证新约束创建成功
- [ ] 已测试手动末班打卡功能
- [ ] 已测试自动末班打卡功能(凌晨5点前)
- [ ] 已测试删除功能
- [ ] 已测试导出功能
- [ ] 功能正常工作

## 技术细节

### 旧约束
```sql
UNIQUE(user_id, punch_time)
```
- 同一用户的同一时间只能打卡一次
- 问题: 无法在不同日期使用相同时间

### 新约束
```sql
UNIQUE(user_id, punch_date, punch_time)
```
- 同一用户在同一日期的同一时间只能打卡一次
- 优点: 允许相同时间在不同日期存在
- 用途: 支持末班打卡复制到前一天

## 相关文件

- 迁移SQL脚本: [`database_migration_unique_constraint.sql`](file:///d:/project/punch_timer/database_migration_unique_constraint.sql)
- 问题分析文档: [`问题修复说明_唯一约束.md`](file:///d:/project/punch_timer/问题修复说明_唯一约束.md)
- 修改的代码文件: [`db_models.py`](file:///d:/project/punch_timer/db_models.py)

## 需要帮助?

如果遇到问题:
1. 检查Render的文档: https://render.com/docs/databases
2. 查看PostgreSQL文档: https://www.postgresql.org/docs/
3. 联系Render支持
