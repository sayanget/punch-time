"""
将JSON数据迁移到SQLite数据库
"""
import json
import sqlite3
from werkzeug.security import generate_password_hash

# 读取JSON数据
print("读取JSON文件...")
with open('users.json', 'r', encoding='utf-8') as f:
    users_data = json.load(f)

with open('punches.json', 'r', encoding='utf-8') as f:
    punches_data = json.load(f)

print(f"找到 {len(users_data)} 个用户")
print(f"找到 {len(punches_data)} 个用户的打卡数据")

# 连接数据库
conn = sqlite3.connect('punch_timer.db')
cursor = conn.cursor()

# 迁移用户数据
print("\n开始迁移用户...")
user_id_map = {}  # 用户名到ID的映射

for username, user_info in users_data.items():
    try:
        # 检查用户是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()
        
        if existing:
            user_id_map[username] = existing[0]
            print(f"  用户 {username} 已存在,ID={existing[0]}")
        else:
            # 插入新用户
            password_hash = user_info['password']
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            user_id = cursor.lastrowid
            user_id_map[username] = user_id
            print(f"  ✓ 迁移用户: {username}, ID={user_id}")
    except Exception as e:
        print(f"  ✗ 迁移用户 {username} 失败: {e}")

conn.commit()

# 迁移打卡数据
print("\n开始迁移打卡记录...")
total_punches = 0

for username, dates in punches_data.items():
    if username not in user_id_map:
        print(f"  警告: 用户 {username} 不存在,跳过其打卡记录")
        continue
    
    user_id = user_id_map[username]
    
    for date, times in dates.items():
        for punch_time in times:
            try:
                # 检查是否已存在
                cursor.execute(
                    "SELECT id FROM punches WHERE user_id = ? AND punch_date = ? AND punch_time = ?",
                    (user_id, date, punch_time)
                )
                if cursor.fetchone():
                    continue  # 已存在,跳过
                
                # 判断是否为末班打卡(凌晨5点前)
                from datetime import datetime
                dt = datetime.fromisoformat(punch_time)
                is_late_shift = dt.hour < 5
                
                # 插入打卡记录
                cursor.execute(
                    "INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift) VALUES (?, ?, ?, ?)",
                    (user_id, date, punch_time, is_late_shift)
                )
                total_punches += 1
            except Exception as e:
                print(f"  ✗ 迁移打卡失败 {username}/{date}/{punch_time}: {e}")

conn.commit()
print(f"\n✓ 迁移完成! 共迁移 {total_punches} 条打卡记录")

# 显示迁移后的统计
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM punches")
punch_count = cursor.fetchone()[0]

print(f"\n数据库统计:")
print(f"  用户总数: {user_count}")
print(f"  打卡记录总数: {punch_count}")

# 检查特定用户
print(f"\n检查用户 1184975:")
cursor.execute("SELECT id, username FROM users WHERE username = '1184975'")
user = cursor.fetchone()
if user:
    print(f"  ✓ 用户存在, ID={user[0]}")
else:
    print(f"  ✗ 用户不存在")

conn.close()
print("\n迁移完成!")
