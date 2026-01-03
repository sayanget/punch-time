# 早上5点前打卡记录测试指南
# Test Guide for Early Morning Punch Records (Before 5 AM)

## 功能说明 (Feature Description)

当员工加班到第二天凌晨时,系统会自动将**早上5点前**的打卡记录复制到前一天的最后一条记录。

When employees work overtime past midnight, the system automatically copies punch records **before 5 AM** to the previous day as the last record.

## 实现细节 (Implementation Details)

### 修改的文件 (Modified Files)
- `app.py` - 主应用文件

### 关键逻辑 (Key Logic)

1. **打卡时判断** (Punch Creation - Line 123-126)
   ```python
   # 自动判断是否为末班打卡(时间在早上5点前)
   hour = int(time_parts[0])
   is_late_shift_auto = hour < 5  # 早上5点前的打卡自动标记为末班打卡
   ```

2. **双记录创建** (Dual Record Creation - Line 135-142)
   ```python
   # 如果是末班打卡,同时添加到前一天的记录中
   if is_late_shift:
       current_date = datetime.strptime(date, '%Y-%m-%d')
       previous_date = current_date - timedelta(days=1)
       previous_date_str = previous_date.strftime('%Y-%m-%d')
       # 添加到前一天的记录中
       add_punch(user_id, previous_date_str, punch_time, is_late_shift)
   ```

3. **删除时同步** (Synchronized Deletion - Line 170-181)
   ```python
   # 检查是否为末班打卡(凌晨5点前的记录)
   if punch_dt.hour < 5:
       # 从前一天的记录中也删除
       delete_punch(user_id, timestamp)
   ```

4. **导出时去重** (Deduplication in Export - Line 219-226)
   ```python
   # 检查是否为末班打卡(凌晨5点前)
   if dt.hour < 5:
       # 如果这个时间戳已经在前一天处理过,跳过
       if t in processed_late_shifts:
           continue
       processed_late_shifts.add(t)
   ```

## 测试场景 (Test Scenarios)

### 场景1: 加班到凌晨3:30
**Scenario 1: Overtime until 3:30 AM**

#### 测试步骤 (Test Steps)

1. **启动应用** (Start Application)
   ```bash
   cd d:\project\punch_timer
   python app.py
   ```

2. **登录系统** (Login)
   - 打开浏览器访问: http://localhost:7777
   - 使用已有账号登录,或注册新账号

3. **添加正常打卡记录** (Add Normal Punch Records)
   - 日期: 2026-01-02
   - 打卡时间:
     - 08:30 (上班)
     - 12:00 (午休)
     - 13:30 (下午上班)
     - 18:00 (正常下班)

4. **添加加班打卡记录** (Add Overtime Punch Record)
   - 日期: 2026-01-03
   - 打卡时间: 03:30 (凌晨加班)

#### 预期结果 (Expected Results)

**2026-01-02 的记录应该有5条:**
- 08:30
- 12:00
- 13:30
- 18:00
- 03:30 (来自第二天的加班打卡)

**2026-01-03 的记录应该有1条:**
- 03:30 (加班打卡)

### 场景2: 边界测试 - 4:59 vs 5:00
**Scenario 2: Boundary Test - 4:59 vs 5:00**

#### 测试步骤 (Test Steps)

1. **测试 4:59** (应该复制到前一天)
   - 日期: 2026-01-04
   - 时间: 04:59
   - 预期: 同时出现在 2026-01-03 和 2026-01-04

2. **测试 5:00** (不应该复制到前一天)
   - 日期: 2026-01-04
   - 时间: 05:00
   - 预期: 只出现在 2026-01-04

### 场景3: 删除测试
**Scenario 3: Deletion Test**

#### 测试步骤 (Test Steps)

1. 添加一条凌晨3:30的打卡记录
2. 验证该记录出现在两天
3. 删除该记录
4. 验证该记录从两天都被删除

## 导出测试 (Export Test)

1. 点击"导出数据"按钮
2. 打开导出的CSV文件
3. 验证:
   - 凌晨的打卡记录只在前一天出现一次(不重复)
   - 时间格式正确
   - 工作时长计算正确

## 数据库验证 (Database Verification)

可以使用以下SQL查询验证数据库中的记录:

```sql
-- 查看所有打卡记录
SELECT 
    u.username,
    p.punch_date,
    p.punch_time,
    p.is_late_shift
FROM punches p
JOIN users u ON p.user_id = u.id
ORDER BY p.punch_time;

-- 查看特定日期的记录
SELECT 
    punch_date,
    punch_time,
    is_late_shift
FROM punches
WHERE user_id = (SELECT id FROM users WHERE username = 'your_username')
    AND punch_date IN ('2026-01-02', '2026-01-03')
ORDER BY punch_time;
```

## 注意事项 (Notes)

1. **时区**: 系统使用本地时间,不涉及时区转换
2. **阈值**: 当前阈值为早上5点(hour < 5)
3. **标记**: 早上5点前的打卡会被标记为 `is_late_shift = True`
4. **唯一性**: 数据库中使用 `(user_id, punch_time)` 作为唯一约束

## 常见问题 (FAQ)

### Q: 为什么选择5点作为阈值?
A: 5点是一个合理的分界点,大多数夜班工作会在5点前结束。

### Q: 如果删除了一条早上5点前的记录,会发生什么?
A: 系统会自动从两个日期(当天和前一天)都删除该记录。

### Q: 导出的CSV文件中会有重复记录吗?
A: 不会,导出功能已经实现了去重逻辑。

### Q: 可以手动标记末班打卡吗?
A: 可以,在添加打卡时可以手动勾选"末班打卡"选项。

## 修改历史 (Change History)

- 2026-01-02: 将阈值从6点改为5点
- 原始实现: 使用6点作为阈值
