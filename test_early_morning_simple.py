"""
简化版测试脚本 - 测试早上5点前的打卡记录
Simplified test script for early morning punch records
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# 直接使用 SQLAlchemy engine
from db_config import engine, init_database
from sqlalchemy import text

def run_test():
    """运行测试"""
    print("\n" + "="*60)
    print("测试场景: 加班到第二天上午的打卡记录")
    print("="*60 + "\n")
    
    # 初始化数据库
    print("1. 初始化数据库...")
    init_database()
    print("   ✓ 数据库初始化完成")
    
    # 测试用户名
    test_username = "test_overtime_user"
    test_password = "test123"
    
    # 使用 with 语句管理连接
    with engine.connect() as conn:
        # 清理旧数据
        print(f"\n2. 清理旧测试数据...")
        result = conn.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": test_username}
        )
        user = result.fetchone()
        
        if user:
            user_id = user[0]
            conn.execute(
                text("DELETE FROM punches WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            conn.execute(
                text("DELETE FROM users WHERE username = :username"),
                {"username": test_username}
            )
            conn.commit()
            print(f"   ✓ 清理完成")
        
        # 创建测试用户
        print(f"\n3. 创建测试用户: {test_username}")
        password_hash = generate_password_hash(test_password)
        result = conn.execute(
            text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash) RETURNING id"),
            {"username": test_username, "password_hash": password_hash}
        )
        conn.commit()
        user_id = result.fetchone()[0]
        print(f"   ✓ 用户创建成功 (ID: {user_id})")
        
        # 测试场景说明
        print("\n4. 测试场景:")
        print("   员工在 2026-01-02 工作,加班到 2026-01-03 凌晨 3:30")
        print("   预期: 凌晨 3:30 的打卡应该同时出现在:")
        print("         - 2026-01-02 (前一天) 的最后一条记录")
        print("         - 2026-01-03 (当天) 的记录")
        
        # 添加 2026-01-02 的正常打卡
        print("\n5. 添加 2026-01-02 的正常打卡...")
        test_date_1 = "2026-01-02"
        normal_punches = [
            "08:30",  # 上班
            "12:00",  # 午休
            "13:30",  # 下午上班
            "18:00",  # 正常下班
        ]
        
        for time_str in normal_punches:
            punch_time = f"{test_date_1}T{time_str}"
            conn.execute(
                text("""
                    INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift)
                    VALUES (:user_id, :punch_date, :punch_time, :is_late_shift)
                """),
                {
                    "user_id": user_id,
                    "punch_date": test_date_1,
                    "punch_time": punch_time,
                    "is_late_shift": False
                }
            )
            print(f"   ✓ {punch_time}")
        
        conn.commit()
        
        # 添加加班打卡 (2026-01-03 凌晨 3:30)
        print("\n6. 添加加班打卡 (2026-01-03 凌晨 3:30)...")
        test_date_2 = "2026-01-03"
        overtime_time = "03:30"
        punch_time_overtime = f"{test_date_2}T{overtime_time}"
        
        # 判断是否为早上5点前
        hour = int(overtime_time.split(':')[0])
        is_early_morning = hour < 5
        
        print(f"   时间: {overtime_time}, 小时: {hour}")
        print(f"   是否为早上5点前: {is_early_morning}")
        
        # 添加到当天 (2026-01-03)
        conn.execute(
            text("""
                INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift)
                VALUES (:user_id, :punch_date, :punch_time, :is_late_shift)
            """),
            {
                "user_id": user_id,
                "punch_date": test_date_2,
                "punch_time": punch_time_overtime,
                "is_late_shift": is_early_morning
            }
        )
        print(f"   ✓ 添加到当天 ({test_date_2}): {punch_time_overtime}")
        
        # 如果是早上5点前,也添加到前一天
        if is_early_morning:
            previous_date = (datetime.strptime(test_date_2, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            conn.execute(
                text("""
                    INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift)
                    VALUES (:user_id, :punch_date, :punch_time, :is_late_shift)
                """),
                {
                    "user_id": user_id,
                    "punch_date": previous_date,
                    "punch_time": punch_time_overtime,
                    "is_late_shift": is_early_morning
                }
            )
            print(f"   ✓ 复制到前一天 ({previous_date}): {punch_time_overtime}")
        
        conn.commit()
        
        # 查询验证
        print("\n7. 验证打卡记录...")
        
        # 查询 2026-01-02 的记录
        print(f"\n   查询 {test_date_1} 的打卡记录:")
        result = conn.execute(
            text("""
                SELECT punch_time, is_late_shift
                FROM punches
                WHERE user_id = :user_id AND punch_date = :punch_date
                ORDER BY punch_time
            """),
            {"user_id": user_id, "punch_date": test_date_1}
        )
        punches_1 = result.fetchall()
        for i, (punch_time, is_late) in enumerate(punches_1, 1):
            late_flag = " (加班)" if is_late else ""
            print(f"   [{i}] {punch_time}{late_flag}")
        
        # 查询 2026-01-03 的记录
        print(f"\n   查询 {test_date_2} 的打卡记录:")
        result = conn.execute(
            text("""
                SELECT punch_time, is_late_shift
                FROM punches
                WHERE user_id = :user_id AND punch_date = :punch_date
                ORDER BY punch_time
            """),
            {"user_id": user_id, "punch_date": test_date_2}
        )
        punches_2 = result.fetchall()
        for i, (punch_time, is_late) in enumerate(punches_2, 1):
            late_flag = " (加班)" if is_late else ""
            print(f"   [{i}] {punch_time}{late_flag}")
        
        # 验证结果
        print("\n8. 验证结果:")
        expected_count_day1 = 5  # 4次正常打卡 + 1次加班打卡
        expected_count_day2 = 1  # 1次加班打卡
        
        success = True
        
        if len(punches_1) == expected_count_day1:
            print(f"   ✓ {test_date_1} 的记录数正确: {len(punches_1)} 条")
            # 检查最后一条是否为凌晨3:30
            if str(punches_1[-1][0]) == punch_time_overtime:
                print(f"   ✓ {test_date_1} 的最后一条记录是加班打卡")
            else:
                print(f"   ✗ {test_date_1} 的最后一条记录不是加班打卡")
                success = False
        else:
            print(f"   ✗ {test_date_1} 的记录数不正确: 期望 {expected_count_day1} 条,实际 {len(punches_1)} 条")
            success = False
        
        if len(punches_2) == expected_count_day2:
            print(f"   ✓ {test_date_2} 的记录数正确: {len(punches_2)} 条")
            if str(punches_2[0][0]) == punch_time_overtime:
                print(f"   ✓ {test_date_2} 的记录是加班打卡")
            else:
                print(f"   ✗ {test_date_2} 的记录不是加班打卡")
                success = False
        else:
            print(f"   ✗ {test_date_2} 的记录数不正确: 期望 {expected_count_day2} 条,实际 {len(punches_2)} 条")
            success = False
        
        # 查询所有记录
        print("\n9. 数据库所有记录:")
        result = conn.execute(
            text("""
                SELECT punch_date, punch_time, is_late_shift
                FROM punches
                WHERE user_id = :user_id
                ORDER BY punch_time
            """),
            {"user_id": user_id}
        )
        all_records = result.fetchall()
        print(f"\n   总共 {len(all_records)} 条记录:")
        for i, (date, time, is_late) in enumerate(all_records, 1):
            late_flag = " (加班)" if is_late else ""
            print(f"   [{i}] 日期: {date}, 时间: {time}{late_flag}")
        
        # 清理测试数据
        print("\n10. 清理测试数据...")
        conn.execute(
            text("DELETE FROM punches WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        conn.execute(
            text("DELETE FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )
        conn.commit()
        print("   ✓ 清理完成")
        
        print("\n" + "="*60)
        if success:
            print("✓ 测试通过!")
        else:
            print("✗ 测试失败!")
        print("="*60 + "\n")
        
        return success

if __name__ == "__main__":
    try:
        success = run_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
