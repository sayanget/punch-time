"""
使用真实用户数据测试导出功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from db_models import get_all_users, get_user_punches
import json

print("=" * 60)
print("检查数据库中的所有用户和打卡数据")
print("=" * 60)

# 获取所有用户
users = get_all_users()
print(f"\n找到 {len(users)} 个用户:")
for user in users:
    print(f"  - ID: {user[0]}, 用户名: {user[1]}")

if not users:
    print("\n❌ 数据库中没有用户！")
    sys.exit(1)

# 测试每个用户的导出
for user in users:
    user_id = user[0]
    username = user[1]
    
    print(f"\n{'='*60}")
    print(f"测试用户: {username} (ID: {user_id})")
    print(f"{'='*60}")
    
    try:
        # 获取用户打卡数据
        punches = get_user_punches(user_id)
        print(f"打卡日期数: {len(punches)}")
        
        if not punches:
            print("  该用户没有打卡记录")
            continue
        
        # 显示数据结构
        for date, records in list(punches.items())[:2]:  # 只显示前2天
            print(f"\n  日期: {date}")
            print(f"  记录数: {len(records)}")
            print(f"  记录类型: {type(records)}")
            
            for i, record in enumerate(records[:3]):  # 只显示前3条
                print(f"    记录 {i+1}:")
                print(f"      类型: {type(record)}")
                print(f"      内容: {record}")
                
                # 检查是否为字典
                if isinstance(record, dict):
                    time_val = record.get('time')
                    print(f"      time值: {time_val} (类型: {type(time_val)})")
                    if time_val is None:
                        print(f"      ⚠️  WARNING: time值为None!")
        
        # 现在测试导出
        print(f"\n测试导出功能...")
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = username
            
            response = client.get('/api/export')
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                if 'text/csv' in response.content_type:
                    print(f"  ✅ 导出成功!")
                    content = response.data.decode('utf-8-sig')
                    lines = content.split('\n')
                    print(f"  CSV行数: {len(lines)}")
                    print(f"  前3行:")
                    for line in lines[:3]:
                        print(f"    {line}")
                else:
                    print(f"  ⚠️  响应类型不是CSV: {response.content_type}")
                    print(f"  响应内容: {response.data.decode('utf-8')[:200]}")
            else:
                print(f"  ❌ 导出失败!")
                print(f"  响应: {response.data.decode('utf-8')[:500]}")
                
    except Exception as e:
        print(f"  ❌ 处理用户 {username} 时出错:")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        import traceback
        print(f"\n  完整堆栈:")
        traceback.print_exc()

print(f"\n{'='*60}")
print("测试完成")
print(f"{'='*60}")
