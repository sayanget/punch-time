"""
直接测试导出功能并捕获详细错误
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from db_models import get_user_punches, get_user_id_by_username, add_punch
from datetime import datetime

# 创建测试数据
print("创建测试用户和数据...")
with app.app_context():
    # 模拟一个已登录的用户
    test_username = 'testuser123'
    
    # 创建测试客户端
    with app.test_client() as client:
        # 设置session
        with client.session_transaction() as sess:
            sess['user_id'] = test_username
        
        # 首先检查用户是否存在，如果不存在就创建
        from db_models import user_exists, create_user
        from werkzeug.security import generate_password_hash
        
        if not user_exists(test_username):
            print(f"创建测试用户: {test_username}")
            create_user(test_username, generate_password_hash('test123'))
        
        user_id = get_user_id_by_username(test_username)
        print(f"用户ID: {user_id}")
        
        # 添加一些测试打卡数据
        test_date = datetime.now().strftime('%Y-%m-%d')
        test_time1 = f"{test_date}T08:30"
        test_time2 = f"{test_date}T12:00"
        
        try:
            add_punch(user_id, test_date, test_time1, False, 39.9042, 116.4074, "Beijing Office")
            add_punch(user_id, test_date, test_time2, False, 39.9042, 116.4074, "Beijing Office")
            print(f"添加了测试打卡数据")
        except Exception as e:
            print(f"添加数据时出错（可能已存在）: {e}")
        
        # 获取打卡数据查看格式
        punches = get_user_punches(user_id)
        print(f"\n打卡数据格式:")
        for date, records in list(punches.items())[:1]:
            print(f"  日期: {date}")
            print(f"  记录类型: {type(records)}")
            if records:
                print(f"  第一条记录类型: {type(records[0])}")
                print(f"  第一条记录内容: {records[0]}")
        
        # 测试导出端点
        print("\n\n测试导出端点...")
        try:
            response = client.get('/api/export')
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                if 'text/csv' in response.content_type:
                    print("✅ 导出成功!")
                    content = response.data.decode('utf-8-sig')
                    print(f"\nCSV内容预览:\n{content[:500]}")
                else:
                    print(f"响应类型: {response.content_type}")
                    print(f"响应内容: {response.data.decode('utf-8')[:500]}")
            else:
                print(f"❌ 导出失败!")
                print(f"响应: {response.data.decode('utf-8')}")
        except Exception as e:
            print(f"❌ 发生异常: {type(e).__name__}: {str(e)}")
            import traceback
            print("\n完整错误堆栈:")
            traceback.print_exc()
