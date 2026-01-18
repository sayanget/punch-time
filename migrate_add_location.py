#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加地理位置字段
为punches表添加latitude, longitude, location_name字段
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取数据库URL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///punch_timer.db')

# 修复Heroku/Render的postgres://协议问题
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
elif DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)

def check_column_exists(engine, table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_add_location_fields():
    """添加地理位置字段到punches表"""
    try:
        # 创建数据库引擎
        if DATABASE_URL.startswith('sqlite'):
            engine = create_engine(
                DATABASE_URL,
                connect_args={'check_same_thread': False}
            )
        else:
            engine = create_engine(DATABASE_URL)
        
        logger.info(f"连接到数据库: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite'}")
        
        with engine.connect() as conn:
            # 检查表是否存在
            inspector = inspect(engine)
            if 'punches' not in inspector.get_table_names():
                logger.error("错误: punches表不存在！")
                return False
            
            # 检查并添加字段
            fields_to_add = []
            
            if not check_column_exists(engine, 'punches', 'latitude'):
                fields_to_add.append('latitude')
            else:
                logger.info("✓ latitude字段已存在")
            
            if not check_column_exists(engine, 'punches', 'longitude'):
                fields_to_add.append('longitude')
            else:
                logger.info("✓ longitude字段已存在")
            
            if not check_column_exists(engine, 'punches', 'location_name'):
                fields_to_add.append('location_name')
            else:
                logger.info("✓ location_name字段已存在")
            
            if not fields_to_add:
                logger.info("\n✓ 所有地理位置字段已存在，无需迁移")
                return True
            
            logger.info(f"\n需要添加的字段: {', '.join(fields_to_add)}")
            
            # 根据数据库类型执行不同的SQL
            if DATABASE_URL.startswith('sqlite'):
                logger.info("\n使用SQLite迁移...")
                
                if 'latitude' in fields_to_add:
                    logger.info("添加 latitude 字段...")
                    conn.execute(text("ALTER TABLE punches ADD COLUMN latitude REAL"))
                    conn.commit()
                    logger.info("✓ latitude字段添加成功")
                
                if 'longitude' in fields_to_add:
                    logger.info("添加 longitude 字段...")
                    conn.execute(text("ALTER TABLE punches ADD COLUMN longitude REAL"))
                    conn.commit()
                    logger.info("✓ longitude字段添加成功")
                
                if 'location_name' in fields_to_add:
                    logger.info("添加 location_name 字段...")
                    conn.execute(text("ALTER TABLE punches ADD COLUMN location_name TEXT"))
                    conn.commit()
                    logger.info("✓ location_name字段添加成功")
            
            else:
                logger.info("\n使用PostgreSQL迁移...")
                
                if 'latitude' in fields_to_add:
                    logger.info("添加 latitude 字段...")
                    conn.execute(text("ALTER TABLE punches ADD COLUMN latitude DOUBLE PRECISION"))
                    conn.commit()
                    logger.info("✓ latitude字段添加成功")
                
                if 'longitude' in fields_to_add:
                    logger.info("添加 longitude 字段...")
                    conn.execute(text("ALTER TABLE punches ADD COLUMN longitude DOUBLE PRECISION"))
                    conn.commit()
                    logger.info("✓ longitude字段添加成功")
                
                if 'location_name' in fields_to_add:
                    logger.info("添加 location_name 字段...")
                    conn.execute(text("ALTER TABLE punches ADD COLUMN location_name VARCHAR(500)"))
                    conn.commit()
                    logger.info("✓ location_name字段添加成功")
            
            # 验证字段已添加
            logger.info("\n验证迁移结果...")
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('punches')]
            
            success = all(field in columns for field in ['latitude', 'longitude', 'location_name'])
            
            if success:
                logger.info("\n" + "="*60)
                logger.info("✓ 数据库迁移成功完成！")
                logger.info("="*60)
                logger.info("\n已添加的字段:")
                logger.info("  - latitude (纬度)")
                logger.info("  - longitude (经度)")
                logger.info("  - location_name (地点名称)")
                logger.info("\n现有记录的这些字段值为 NULL")
                logger.info("新打卡记录将包含地理位置信息")
                return True
            else:
                logger.error("\n✗ 迁移验证失败")
                return False
                
    except Exception as e:
        logger.error(f"\n✗ 数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def rollback_migration():
    """回滚迁移：删除地理位置字段"""
    try:
        if DATABASE_URL.startswith('sqlite'):
            engine = create_engine(
                DATABASE_URL,
                connect_args={'check_same_thread': False}
            )
        else:
            engine = create_engine(DATABASE_URL)
        
        logger.info("开始回滚迁移...")
        
        with engine.connect() as conn:
            if DATABASE_URL.startswith('sqlite'):
                logger.warning("SQLite不支持DROP COLUMN，需要手动处理")
                logger.info("建议：重新创建表或使用备份恢复")
            else:
                logger.info("删除 latitude 字段...")
                conn.execute(text("ALTER TABLE punches DROP COLUMN IF EXISTS latitude"))
                
                logger.info("删除 longitude 字段...")
                conn.execute(text("ALTER TABLE punches DROP COLUMN IF EXISTS longitude"))
                
                logger.info("删除 location_name 字段...")
                conn.execute(text("ALTER TABLE punches DROP COLUMN IF EXISTS location_name"))
                
                conn.commit()
                logger.info("✓ 回滚成功")
        
        return True
    except Exception as e:
        logger.error(f"回滚失败: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("打卡记录地理位置功能 - 数据库迁移")
    print("="*60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        print("\n⚠️  警告: 即将回滚迁移（删除地理位置字段）")
        response = input("确认回滚? (yes/no): ")
        if response.lower() == 'yes':
            rollback_migration()
        else:
            print("已取消回滚")
    else:
        print("\n此脚本将为punches表添加以下字段:")
        print("  - latitude (纬度)")
        print("  - longitude (经度)")
        print("  - location_name (地点名称)")
        print("\n现有数据不会受到影响（字段值为NULL）")
        
        response = input("\n继续迁移? (yes/no): ")
        if response.lower() == 'yes':
            success = migrate_add_location_fields()
            sys.exit(0 if success else 1)
        else:
            print("已取消迁移")
            sys.exit(0)
