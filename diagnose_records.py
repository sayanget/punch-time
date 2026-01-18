#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断脚本：检查打卡记录显示问题
用于Render Shell中运行
"""

import os
import sys
from db_config import get_db, DATABASE_URL
from db_models import get_user_punches, get_user_id_by_username
from sqlalchemy import text, inspect

def check_database_connection():
    """检查数据库连接"""
    print("\n" + "="*60)
    print("1. 检查数据库连接")
    print("="*60)
    
    try:
        db = get_db()
        result = db.execute(text("SELECT 1"))
        print("✓ 数据库连接成功")
        print(f"✓ 数据库URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite'}")
        db.close()
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def check_table_structure():
    """检查表结构"""
    print("\n" + "="*60)
    print("2. 检查punches表结构")
    print("="*60)
    
    try:
        from db_config import engine
        inspector = inspect(engine)
        
        if 'punches' not in inspector.get_table_names():
            print("✗ punches表不存在！")
            return False
        
        columns = inspector.get_columns('punches')
        print(f"✓ punches表存在，共有 {len(columns)} 个字段：")
        
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # 检查位置字段
        col_names = [col['name'] for col in columns]
        has_location = all(field in col_names for field in ['latitude', 'longitude', 'location_name'])
        
        if has_location:
            print("\n✓ 地理位置字段已存在")
        else:
            print("\n⚠️  地理位置字段不存在（这是正常的，如果还没执行迁移）")
        
        return True
    except Exception as e:
        print(f"✗ 检查表结构失败: {e}")
        return False

def check_users():
    """检查用户数据"""
    print("\n" + "="*60)
    print("3. 检查用户数据")
    print("="*60)
    
    try:
        db = get_db()
        result = db.execute(text("SELECT id, username FROM users"))
        users = result.fetchall()
        
        if not users:
            print("⚠️  没有用户数据")
            return False
        
        print(f"✓ 找到 {len(users)} 个用户：")
        for user in users:
            print(f"  - ID: {user[0]}, 用户名: {user[1]}")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ 检查用户失败: {e}")
        return False

def check_punch_records():
    """检查打卡记录"""
    print("\n" + "="*60)
    print("4. 检查打卡记录")
    print("="*60)
    
    try:
        db = get_db()
        
        # 检查总记录数
        result = db.execute(text("SELECT COUNT(*) FROM punches"))
        total_count = result.fetchone()[0]
        print(f"✓ 数据库中共有 {total_count} 条打卡记录")
        
        if total_count == 0:
            print("⚠️  没有打卡记录")
            db.close()
            return False
        
        # 按用户分组统计
        result = db.execute(text("""
            SELECT user_id, COUNT(*) as count 
            FROM punches 
            GROUP BY user_id
        """))
        user_counts = result.fetchall()
        
        print(f"\n按用户统计：")
        for user_id, count in user_counts:
            print(f"  - 用户ID {user_id}: {count} 条记录")
        
        # 显示最近的5条记录
        result = db.execute(text("""
            SELECT user_id, punch_date, punch_time 
            FROM punches 
            ORDER BY punch_time DESC 
            LIMIT 5
        """))
        recent = result.fetchall()
        
        print(f"\n最近的5条记录：")
        for record in recent:
            print(f"  - 用户ID: {record[0]}, 日期: {record[1]}, 时间: {record[2]}")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ 检查打卡记录失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_user_punches():
    """测试get_user_punches函数"""
    print("\n" + "="*60)
    print("5. 测试get_user_punches函数")
    print("="*60)
    
    try:
        # 获取第一个用户
        db = get_db()
        result = db.execute(text("SELECT id, username FROM users LIMIT 1"))
        user = result.fetchone()
        db.close()
        
        if not user:
            print("⚠️  没有用户，无法测试")
            return False
        
        user_id, username = user[0], user[1]
        print(f"测试用户: {username} (ID: {user_id})")
        
        # 调用get_user_punches
        punches = get_user_punches(user_id)
        
        if not punches:
            print("✗ get_user_punches返回空数据")
            return False
        
        print(f"✓ get_user_punches返回了 {len(punches)} 个日期的数据")
        
        # 显示数据结构
        for date, records in list(punches.items())[:3]:  # 只显示前3天
            print(f"\n日期: {date}")
            print(f"  记录数: {len(records)}")
            if records:
                first_record = records[0]
                print(f"  第一条记录: {first_record}")
        
        return True
    except Exception as e:
        print(f"✗ 测试get_user_punches失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("打卡记录显示问题诊断脚本")
    print("="*60)
    
    results = {
        "数据库连接": check_database_connection(),
        "表结构": check_table_structure(),
        "用户数据": check_users(),
        "打卡记录": check_punch_records(),
        "API函数": test_get_user_punches()
    }
    
    print("\n" + "="*60)
    print("诊断结果汇总")
    print("="*60)
    
    for check, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{check}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ 所有检查通过！")
        print("如果前端仍然看不到记录，请检查：")
        print("1. 浏览器控制台是否有JavaScript错误")
        print("2. 网络请求是否成功（F12 → Network）")
        print("3. 清除浏览器缓存并刷新")
    else:
        print("✗ 发现问题，请根据上述错误信息进行修复")
    print("="*60)

if __name__ == "__main__":
    main()
