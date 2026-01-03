"""测试用户ID查询"""
import sys
sys.path.insert(0, '.')

from db_models import get_user_by_username, get_user_id_by_username
import sqlite3

print("=== 直接SQLite查询 ===")
conn = sqlite3.connect('punch_timer.db')
cursor = conn.cursor()
cursor.execute("SELECT id, username FROM users WHERE username = ?", ('1184975',))
result = cursor.fetchone()
print(f"SQLite结果: {result}")
conn.close()

print("\n=== 使用db_models查询 ===")
try:
    user = get_user_by_username('1184975')
    print(f"get_user_by_username结果: {user}")
    print(f"类型: {type(user)}")
    if user:
        print(f"user[0] (ID): {user[0]}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 使用get_user_id_by_username ===")
try:
    user_id = get_user_id_by_username('1184975')
    print(f"用户ID: {user_id}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
