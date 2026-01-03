"""
简化的数据库连接测试脚本
"""
import os
import sys

# 设置数据库连接字符串
DATABASE_URL = "postgresql://postgres.jkoqqvuddfetdwnuaobc:Coyd1uNhObsGDfu9@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
os.environ['DATABASE_URL'] = DATABASE_URL

print("=" * 60)
print("Supabase数据库连接测试")
print("=" * 60)

try:
    from db_config import init_database
    from db_models import create_user, get_all_users, user_exists
    
    print("\n✅ 成功导入数据库模块")
    
    # 测试1: 查询所有用户
    print("\n" + "=" * 60)
    print("测试1: 查询现有用户")
    print("=" * 60)
    
    users = get_all_users()
    print(f"✅ 数据库中共有 {len(users)} 个用户")
    
    if users:
        print("\n用户列表:")
        for user in users[:5]:
            print(f"  - ID: {user[0]}, 用户名: {user[1]}")
        if len(users) > 5:
            print(f"  ... 还有 {len(users) - 5} 个用户")
    
    # 测试2: 创建测试用户
    print("\n" + "=" * 60)
    print("测试2: 创建测试用户")
    print("=" * 60)
    
    test_username = "test_user_" + str(os.urandom(4).hex())
    
    if not user_exists(test_username):
        user_id = create_user(test_username, "test_password_hash_123")
        print(f"✅ 成功创建测试用户: {test_username} (ID: {user_id})")
    else:
        print(f"⚠️  测试用户已存在: {test_username}")
    
    # 再次查询确认
    users = get_all_users()
    print(f"✅ 当前数据库中共有 {len(users)} 个用户")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过! Supabase数据库配置正确!")
    print("=" * 60)
    
    print("\n✅ 下一步操作:")
    print("1. 运行 'python migrate_to_db.py' 迁移现有JSON数据")
    print("2. 运行 'python app.py' 启动应用")
    print("3. 在Render中配置DATABASE_URL环境变量并部署")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    print("\n💡 提示:")
    print("1. 确保已设置DATABASE_URL环境变量")
    print("2. 检查数据库密码是否正确")
    print("3. 确保网络可以访问Supabase服务器")
    import traceback
    traceback.print_exc()
    sys.exit(1)
