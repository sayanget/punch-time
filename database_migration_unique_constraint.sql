-- 数据库迁移脚本: 修复末班打卡唯一约束问题
-- 执行时间: 2026-01-02
-- 目的: 允许相同的punch_time在不同的punch_date存在

-- 步骤1: 删除旧的唯一约束
-- 注意: PostgreSQL中约束名称可能是自动生成的,需要先查询实际名称
-- 查询约束名称:
-- SELECT conname FROM pg_constraint WHERE conrelid = 'punches'::regclass AND contype = 'u';

-- 删除唯一约束 (根据实际约束名称调整)
ALTER TABLE punches DROP CONSTRAINT IF EXISTS punches_user_id_punch_time_key;

-- 步骤2: 添加新的唯一约束
-- 新约束: 同一用户、同一日期、同一时间不能重复
-- 但允许同一用户、同一时间在不同日期存在(用于末班打卡)
ALTER TABLE punches ADD CONSTRAINT punches_user_id_punch_date_punch_time_key 
    UNIQUE (user_id, punch_date, punch_time);

-- 验证约束已创建
-- SELECT conname, contype FROM pg_constraint WHERE conrelid = 'punches'::regclass;

-- 说明:
-- 1. 这个修改允许凌晨打卡同时存在于两个不同的日期
-- 2. 例如: 2026-01-03 03:30 可以同时出现在 2026-01-02 和 2026-01-03
-- 3. 但同一日期内,同一时间仍然不能重复打卡
