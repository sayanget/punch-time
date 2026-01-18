-- Supabase数据库迁移：添加地理位置字段
-- 执行日期：2026-01-18
-- 功能：为punches表添加latitude, longitude, location_name字段

-- 检查并添加latitude字段
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'punches' AND column_name = 'latitude'
    ) THEN
        ALTER TABLE punches ADD COLUMN latitude DOUBLE PRECISION;
        RAISE NOTICE '✓ 已添加 latitude 字段';
    ELSE
        RAISE NOTICE '✓ latitude 字段已存在';
    END IF;
END $$;

-- 检查并添加longitude字段
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'punches' AND column_name = 'longitude'
    ) THEN
        ALTER TABLE punches ADD COLUMN longitude DOUBLE PRECISION;
        RAISE NOTICE '✓ 已添加 longitude 字段';
    ELSE
        RAISE NOTICE '✓ longitude 字段已存在';
    END IF;
END $$;

-- 检查并添加location_name字段
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'punches' AND column_name = 'location_name'
    ) THEN
        ALTER TABLE punches ADD COLUMN location_name VARCHAR(500);
        RAISE NOTICE '✓ 已添加 location_name 字段';
    ELSE
        RAISE NOTICE '✓ location_name 字段已存在';
    END IF;
END $$;

-- 验证迁移结果
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'punches' 
    AND column_name IN ('latitude', 'longitude', 'location_name')
ORDER BY column_name;

-- 显示成功消息
DO $$ 
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '✓ 数据库迁移完成！';
    RAISE NOTICE '========================================';
    RAISE NOTICE '已添加的字段：';
    RAISE NOTICE '  - latitude (纬度)';
    RAISE NOTICE '  - longitude (经度)';
    RAISE NOTICE '  - location_name (地点名称)';
    RAISE NOTICE '';
    RAISE NOTICE '现有记录的这些字段值为 NULL';
    RAISE NOTICE '新打卡记录将包含地理位置信息';
END $$;
