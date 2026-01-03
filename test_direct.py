"""
直接使用SQLAlchemy测试Supabase连接
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "postgresql://postgres.jkoqqvuddfetdwnuaobc:Coyd1uNhObsGDfu9@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

print("=" * 60)
print("Supabase数据库连接测试 (直接连接)")
print("=" * 60)

try:
    # 创建引擎
    engine = create_engine(DATABASE_URL, echo=False)
    
    print("\n✅ 成功创建数据库引擎")
    
    # 测试连接
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ 数据库连接成功!")
        print(f"   PostgreSQL版本: {version[:80]}...")
        
        # 检查users表
        print("\n" + "=" * 60)
        print("检查数据库表结构")
        print("=" * 60)
        
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        users_columns = result.fetchall()
        
        if users_columns:
            print("\n✅ users表结构:")
            for col in users_columns:
                print(f"   - {col[0]}: {col[1]}")
        else:
            print("\n❌ users表不存在")
        
        # 检查punches表
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'punches'
            ORDER BY ordinal_position
        """))
        punches_columns = result.fetchall()
        
        if punches_columns:
            print("\n✅ punches表结构:")
            for col in punches_columns:
                print(f"   - {col[0]}: {col[1]}")
        else:
            print("\n❌ punches表不存在")
        
        # 统计用户数
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.fetchone()[0]
        print(f"\n✅ 数据库中共有 {user_count} 个用户")
        
        # 统计打卡记录数
        result = conn.execute(text("SELECT COUNT(*) FROM punches"))
        punch_count = result.fetchone()[0]
        print(f"✅ 数据库中共有 {punch_count} 条打卡记录")
    
    print("\n" + "=" * 60)
    print("🎉 数据库连接测试成功!")
    print("=" * 60)
    
    print("\n✅ 下一步操作:")
    print("1. 运行 'python migrate_to_db.py' 迁移现有JSON数据")
    print("2. 配置.env文件或环境变量")
    print("3. 运行 'python app.py' 启动应用")
    
except Exception as e:
    print(f"\n❌ 连接失败: {e}")
    import traceback
    traceback.print_exc()
