"""
测试早上5点前的打卡记录复制到前一天的功能
Test script for copying punch records before 5 AM to the previous day
"""
from datetime import datetime, timedelta
from db_config import init_database, get_db
from db_models import (
    create_user, get_user_by_username, get_user_id_by_username,
    add_punch, get_user_punches, get_punches_by_date, delete_punch
)
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def cleanup_test_data(username):
    """清理测试数据"""
    from db_config import engine
    try:
        # 使用 engine.connect() 而不是 get_db()
        with engine.connect() as conn:
            # 获取用户ID
            result = conn.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": username}
            )
            user = result.fetchone()
            
            if user:
                user_id = user[0]
                # 删除该用户的所有打卡记录
                conn.execute(
                    text("DELETE FROM punches WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                # 删除用户
                conn.execute(
                    text("DELETE FROM users WHERE username = :username"),
                    {"username": username}
                )
                conn.commit()
                print(f"✓ 清理测试用户 {username} 的数据")
    except Exception as e:
        print(f"✗ 清理数据失败: {e}")

def test_early_morning_punch():
    """测试早上5点前的打卡记录"""
    print("\n" + "="*60)
    print("测试场景: 加班到第二天上午的打卡记录")
    print("="*60 + "\n")
    
    # 初始化数据库
    init_database()
    
    # 测试用户名
    test_username = "test_overtime_user"
    
    # 清理可能存在的旧测试数据
    cleanup_test_data(test_username)
    
    # 创建测试用户
    print("1. 创建测试用户...")
    try:
        password_hash = generate_password_hash("test123")
        user_id = create_user(test_username, password_hash)
        print(f"   ✓ 创建用户成功: {test_username} (ID: {user_id})")
    except Exception as e:
        print(f"   ✗ 创建用户失败: {e}")
        return
    
    # 获取用户ID
    user_id = get_user_id_by_username(test_username)
    if not user_id:
        print("   ✗ 无法获取用户ID")
        return
    
    # 测试场景: 2026-01-02 加班到 2026-01-03 凌晨
    print("\n2. 测试场景设置:")
    print("   员工在 2026-01-02 工作,加班到 2026-01-03 凌晨 3:30")
    print("   预期: 凌晨 3:30 的打卡应该同时出现在:")
    print("         - 2026-01-02 (前一天) 的最后一条记录")
    print("         - 2026-01-03 (当天) 的记录")
    
    # 添加正常打卡记录 (2026-01-02)
    print("\n3. 添加 2026-01-02 的正常打卡记录...")
    test_date_1 = "2026-01-02"
    punches_day1 = [
        ("08:30", False),  # 上班
        ("12:00", False),  # 午休
        ("13:30", False),  # 下午上班
        ("18:00", False),  # 正常下班
    ]
    
    for time_str, is_late in punches_day1:
        punch_time = f"{test_date_1}T{time_str}"
        try:
            add_punch(user_id, test_date_1, punch_time, is_late)
            print(f"   ✓ 添加打卡: {punch_time}")
        except Exception as e:
            print(f"   ✗ 添加打卡失败: {e}")
    
    # 添加加班打卡记录 (2026-01-03 凌晨 3:30)
    print("\n4. 添加加班打卡记录 (2026-01-03 凌晨 3:30)...")
    test_date_2 = "2026-01-03"
    overtime_time = "03:30"
    punch_time_overtime = f"{test_date_2}T{overtime_time}"
    
    try:
        # 判断是否为早上5点前
        hour = int(overtime_time.split(':')[0])
        is_early_morning = hour < 5
        
        print(f"   时间: {overtime_time}, 小时: {hour}")
        print(f"   是否为早上5点前: {is_early_morning}")
        
        # 添加到当天 (2026-01-03)
        punch_id = add_punch(user_id, test_date_2, punch_time_overtime, is_early_morning)
        print(f"   ✓ 添加到当天 ({test_date_2}): {punch_time_overtime}")
        
        # 如果是早上5点前,也添加到前一天
        if is_early_morning:
            previous_date = (datetime.strptime(test_date_2, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            add_punch(user_id, previous_date, punch_time_overtime, is_early_morning)
            print(f"   ✓ 复制到前一天 ({previous_date}): {punch_time_overtime}")
    except Exception as e:
        print(f"   ✗ 添加加班打卡失败: {e}")
    
    # 验证结果
    print("\n5. 验证打卡记录...")
    
    # 查询 2026-01-02 的记录
    print(f"\n   查询 {test_date_1} 的打卡记录:")
    punches_1 = get_punches_by_date(user_id, test_date_1)
    for i, punch in enumerate(punches_1, 1):
        print(f"   [{i}] {punch}")
    
    # 查询 2026-01-03 的记录
    print(f"\n   查询 {test_date_2} 的打卡记录:")
    punches_2 = get_punches_by_date(user_id, test_date_2)
    for i, punch in enumerate(punches_2, 1):
        print(f"   [{i}] {punch}")
    
    # 验证逻辑
    print("\n6. 验证结果:")
    expected_count_day1 = 5  # 4次正常打卡 + 1次加班打卡
    expected_count_day2 = 1  # 1次加班打卡
    
    if len(punches_1) == expected_count_day1:
        print(f"   ✓ {test_date_1} 的记录数正确: {len(punches_1)} 条")
        # 检查最后一条是否为凌晨3:30
        if punches_1[-1] == punch_time_overtime:
            print(f"   ✓ {test_date_1} 的最后一条记录是加班打卡: {punches_1[-1]}")
        else:
            print(f"   ✗ {test_date_1} 的最后一条记录不是加班打卡: {punches_1[-1]}")
    else:
        print(f"   ✗ {test_date_1} 的记录数不正确: 期望 {expected_count_day1} 条,实际 {len(punches_1)} 条")
    
    if len(punches_2) == expected_count_day2:
        print(f"   ✓ {test_date_2} 的记录数正确: {len(punches_2)} 条")
        if punches_2[0] == punch_time_overtime:
            print(f"   ✓ {test_date_2} 的记录是加班打卡: {punches_2[0]}")
        else:
            print(f"   ✗ {test_date_2} 的记录不是加班打卡: {punches_2[0]}")
    else:
        print(f"   ✗ {test_date_2} 的记录数不正确: 期望 {expected_count_day2} 条,实际 {len(punches_2)} 条")
    
    # 查询数据库原始数据
    print("\n7. 数据库原始数据:")
    from db_config import engine
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT punch_date, punch_time, is_late_shift 
                    FROM punches 
                    WHERE user_id = :user_id 
                    ORDER BY punch_time
                """),
                {"user_id": user_id}
            )
            records = result.fetchall()
            print(f"\n   总共 {len(records)} 条记录:")
            for i, record in enumerate(records, 1):
                print(f"   [{i}] 日期: {record[0]}, 时间: {record[1]}, 是否加班: {record[2]}")
    except Exception as e:
        print(f"   ✗ 查询数据库失败: {e}")
    
    # 清理测试数据
    print("\n8. 清理测试数据...")
    cleanup_test_data(test_username)
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_early_morning_punch()
