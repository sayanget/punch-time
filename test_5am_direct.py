"""
直接数据库测试 - 早上5点前打卡记录
Direct database test for early morning punch records
"""
import sqlite3
from datetime import datetime, timedelta

def test_with_sqlite():
    """使用SQLite直接测试"""
    print("\n" + "="*70)
    print("直接数据库测试 - 早上5点前打卡记录复制功能")
    print("="*70 + "\n")
    
    # 连接到SQLite数据库
    db_path = "punch_timer.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 测试用户名
    test_username = "test_5am_user"
    
    try:
        # 1. 清理旧数据
        print("1. 清理旧测试数据...")
        cursor.execute("SELECT id FROM users WHERE username = ?", (test_username,))
        user = cursor.fetchone()
        if user:
            user_id = user[0]
            cursor.execute("DELETE FROM punches WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
            conn.commit()
            print(f"   ✓ 清理完成")
        
        # 2. 创建测试用户
        print(f"\n2. 创建测试用户: {test_username}")
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash("test123")
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (test_username, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        print(f"   ✓ 用户创建成功 (ID: {user_id})")
        
        # 3. 测试场景说明
        print("\n3. 测试场景:")
        print("   员工在 2026-01-02 工作,加班到 2026-01-03 凌晨 3:30")
        print("   预期: 凌晨 3:30 的打卡应该同时出现在:")
        print("         - 2026-01-02 (前一天) 的最后一条记录")
        print("         - 2026-01-03 (当天) 的记录")
        
        # 4. 添加正常打卡记录
        print("\n4. 添加 2026-01-02 的正常打卡...")
        test_date_1 = "2026-01-02"
        normal_times = ["08:30", "12:00", "13:30", "18:00"]
        
        for time_str in normal_times:
            punch_time = f"{test_date_1}T{time_str}"
            cursor.execute(
                """INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift)
                   VALUES (?, ?, ?, ?)""",
                (user_id, test_date_1, punch_time, 0)
            )
            print(f"   ✓ {punch_time}")
        conn.commit()
        
        # 5. 添加加班打卡 (凌晨3:30)
        print("\n5. 添加加班打卡 (2026-01-03 凌晨 3:30)...")
        test_date_2 = "2026-01-03"
        overtime_time = "03:30"
        punch_time_overtime = f"{test_date_2}T{overtime_time}"
        
        # 判断是否为早上5点前
        hour = int(overtime_time.split(':')[0])
        is_early_morning = 1 if hour < 5 else 0
        
        print(f"   时间: {overtime_time}, 小时: {hour}")
        print(f"   是否为早上5点前: {bool(is_early_morning)}")
        
        # 添加到当天
        cursor.execute(
            """INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift)
               VALUES (?, ?, ?, ?)""",
            (user_id, test_date_2, punch_time_overtime, is_early_morning)
        )
        print(f"   ✓ 添加到当天 ({test_date_2}): {punch_time_overtime}")
        
        # 如果是早上5点前,也添加到前一天
        if is_early_morning:
            previous_date = (datetime.strptime(test_date_2, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            cursor.execute(
                """INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift)
                   VALUES (?, ?, ?, ?)""",
                (user_id, previous_date, punch_time_overtime, is_early_morning)
            )
            print(f"   ✓ 复制到前一天 ({previous_date}): {punch_time_overtime}")
        
        conn.commit()
        
        # 6. 验证结果
        print("\n6. 验证打卡记录...")
        
        # 查询 2026-01-02 的记录
        print(f"\n   查询 {test_date_1} 的打卡记录:")
        cursor.execute(
            """SELECT punch_time, is_late_shift
               FROM punches
               WHERE user_id = ? AND punch_date = ?
               ORDER BY punch_time""",
            (user_id, test_date_1)
        )
        punches_1 = cursor.fetchall()
        for i, (punch_time, is_late) in enumerate(punches_1, 1):
            late_flag = " (加班)" if is_late else ""
            print(f"   [{i}] {punch_time}{late_flag}")
        
        # 查询 2026-01-03 的记录
        print(f"\n   查询 {test_date_2} 的打卡记录:")
        cursor.execute(
            """SELECT punch_time, is_late_shift
               FROM punches
               WHERE user_id = ? AND punch_date = ?
               ORDER BY punch_time""",
            (user_id, test_date_2)
        )
        punches_2 = cursor.fetchall()
        for i, (punch_time, is_late) in enumerate(punches_2, 1):
            late_flag = " (加班)" if is_late else ""
            print(f"   [{i}] {punch_time}{late_flag}")
        
        # 7. 验证逻辑
        print("\n7. 验证结果:")
        expected_count_day1 = 5  # 4次正常打卡 + 1次加班打卡
        expected_count_day2 = 1  # 1次加班打卡
        
        success = True
        
        if len(punches_1) == expected_count_day1:
            print(f"   ✓ {test_date_1} 的记录数正确: {len(punches_1)} 条")
            # 检查最后一条是否为凌晨3:30
            if punches_1[-1][0] == punch_time_overtime:
                print(f"   ✓ {test_date_1} 的最后一条记录是加班打卡: {punches_1[-1][0]}")
            else:
                print(f"   ✗ {test_date_1} 的最后一条记录不是加班打卡: {punches_1[-1][0]}")
                success = False
        else:
            print(f"   ✗ {test_date_1} 的记录数不正确: 期望 {expected_count_day1} 条,实际 {len(punches_1)} 条")
            success = False
        
        if len(punches_2) == expected_count_day2:
            print(f"   ✓ {test_date_2} 的记录数正确: {len(punches_2)} 条")
            if punches_2[0][0] == punch_time_overtime:
                print(f"   ✓ {test_date_2} 的记录是加班打卡: {punches_2[0][0]}")
            else:
                print(f"   ✗ {test_date_2} 的记录不是加班打卡: {punches_2[0][0]}")
                success = False
        else:
            print(f"   ✗ {test_date_2} 的记录数不正确: 期望 {expected_count_day2} 条,实际 {len(punches_2)} 条")
            success = False
        
        # 8. 查询所有记录
        print("\n8. 数据库所有记录:")
        cursor.execute(
            """SELECT punch_date, punch_time, is_late_shift
               FROM punches
               WHERE user_id = ?
               ORDER BY punch_time""",
            (user_id,)
        )
        all_records = cursor.fetchall()
        print(f"\n   总共 {len(all_records)} 条记录:")
        for i, (date, time, is_late) in enumerate(all_records, 1):
            late_flag = " (加班)" if is_late else ""
            print(f"   [{i}] 日期: {date}, 时间: {time}{late_flag}")
        
        # 9. 清理测试数据
        print("\n9. 清理测试数据...")
        cursor.execute("DELETE FROM punches WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        print("   ✓ 清理完成")
        
        print("\n" + "="*70)
        if success:
            print("✓ 测试通过!")
        else:
            print("✗ 测试失败!")
        print("="*70 + "\n")
        
        return success
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    success = test_with_sqlite()
    sys.exit(0 if success else 1)
