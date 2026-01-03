"""
数据库连接测试脚本
用于验证Supabase数据库配置是否正确
"""
import os
from db_config import init_database, get_db
from db_models import create_user, get_all_users, user_exists
from sqlalchemy import text

def test_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("开始测试Supabase数据库连接...")
    print("=" * 50)
    
    # 检查DATABASE_URL环境变量
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///punch_timer.db')
    if db_url.startswith('sqlite'):
        print("⚠️  警告: 当前使用SQLite数据库,而非Supabase PostgreSQL")
        print(f"   DATABASE_URL: {db_url}")
        print("\n请设置DATABASE_URL环境变量为Supabase连接字符串")
        return False
    else:
        print(f"✅ 检测到PostgreSQL连接")
        # 隐藏密码部分
        safe_url = db_url.split('@')[1] if '@' in db_url else db_url
        print(f"   数据库地址: {safe_url}")
    
    print("\n" + "=" * 50)
    print("1. 测试数据库连接...")
    print("=" * 50)
    
    try:
        db = get_db()
        result = db.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ 数据库连接成功!")
        print(f"   PostgreSQL版本: {version[:50]}...")
        db.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("2. 测试表结构...")
    print("=" * 50)
    
    try:
        db = get_db()
        
        # 检查users表
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        users_columns = result.fetchall()
        db.commit()  # 提交事务
        
        if users_columns:
            print("✅ users表结构:")
            for col in users_columns:
                print(f"   - {col[0]}: {col[1]}")
        else:
            print("❌ users表不存在")
            db.close()
            return False
        
        # 检查punches表
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'punches'
            ORDER BY ordinal_position
        """))
        punches_columns = result.fetchall()
        db.commit()  # 提交事务
        
        if punches_columns:
            print("\n✅ punches表结构:")
            for col in punches_columns:
                print(f"   - {col[0]}: {col[1]}")
        else:
            print("❌ punches表不存在")
            db.close()
            return False
        
        # 检查索引
        result = db.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'punches'
        """))
        indexes = result.fetchall()
        db.commit()  # 提交事务
        
        if indexes:
            print("\n✅ punches表索引:")
            for idx in indexes:
                print(f"   - {idx[0]}")
        
        db.close()
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("3. 测试数据操作...")
    print("=" * 50)
    
    try:
        # 测试创建用户
        test_username = "test_user_" + str(os.urandom(4).hex())
        
        if not user_exists(test_username):
            user_id = create_user(test_username, "test_password_hash_123")
            print(f"✅ 成功创建测试用户: {test_username} (ID: {user_id})")
        else:
            print(f"⚠️  测试用户已存在: {test_username}")
        
        # 查询所有用户
        users = get_all_users()
        print(f"✅ 数据库中共有 {len(users)} 个用户")
        
        if users:
            print("\n   用户列表:")
            for user in users[:5]:  # 只显示前5个
                print(f"   - ID: {user[0]}, 用户名: {user[1]}")
            if len(users) > 5:
                print(f"   ... 还有 {len(users) - 5} 个用户")
        
    except Exception as e:
        print(f"❌ 数据操作失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过! Supabase数据库配置正确!")
    print("=" * 50)
    return True

if __name__ == '__main__':
    success = test_connection()
    if not success:
        print("\n💡 提示:")
        print("1. 确保已设置DATABASE_URL环境变量")
        print("2. 检查数据库密码是否正确")
        print("3. 确保网络可以访问Supabase服务器")
        exit(1)
    else:
        print("\n✅ 您现在可以:")
        print("1. 运行 'python migrate_to_db.py' 迁移现有数据")
        print("2. 运行 'python app.py' 启动应用")
        print("3. 部署到Render并配置DATABASE_URL环境变量")
