"""
从Supabase云端数据库同步数据到本地SQLite数据库
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase数据库连接
SUPABASE_URL = "postgresql://postgres.jkoqqvuddfetdwnuaobc:Coyd1uNhObsGDfu9@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

# 本地SQLite数据库
LOCAL_DB = "sqlite:///punch_timer.db"

def sync_from_supabase_to_local():
    """从Supabase同步数据到本地"""
    try:
        # 连接到Supabase
        logger.info("连接到Supabase...")
        supabase_engine = create_engine(SUPABASE_URL.replace('postgresql://', 'postgresql+psycopg://'))
        
        # 连接到本地SQLite
        logger.info("连接到本地SQLite...")
        local_engine = create_engine(LOCAL_DB, connect_args={'check_same_thread': False})
        
        # 备份本地数据库
        logger.info("备份本地数据库...")
        import shutil
        from datetime import datetime
        backup_name = f"punch_timer_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        if os.path.exists('punch_timer.db'):
            shutil.copy2('punch_timer.db', backup_name)
            logger.info(f"✓ 备份已创建: {backup_name}")
        
        # 从Supabase读取数据
        logger.info("\n从Supabase读取数据...")
        with supabase_engine.connect() as conn:
            # 读取用户数据
            users_result = conn.execute(text("SELECT * FROM users ORDER BY id"))
            users = users_result.fetchall()
            logger.info(f"✓ 读取到 {len(users)} 个用户")
            
            # 读取打卡数据
            punches_result = conn.execute(text("SELECT * FROM punches ORDER BY id"))
            punches = punches_result.fetchall()
            logger.info(f"✓ 读取到 {len(punches)} 条打卡记录")
        
        # 清空本地数据库
        logger.info("\n清空本地数据库...")
        with local_engine.connect() as conn:
            conn.execute(text("DELETE FROM punches"))
            conn.execute(text("DELETE FROM users"))
            conn.commit()
            logger.info("✓ 本地数据已清空")
        
        # 写入用户数据到本地
        logger.info("\n写入用户数据到本地...")
        with local_engine.connect() as conn:
            for user in users:
                conn.execute(text("""
                    INSERT INTO users (id, username, password_hash, created_at)
                    VALUES (:id, :username, :password_hash, :created_at)
                """), {
                    'id': user[0],
                    'username': user[1],
                    'password_hash': user[2],
                    'created_at': user[3]
                })
            conn.commit()
            logger.info(f"✓ 已写入 {len(users)} 个用户")
        
        # 写入打卡数据到本地
        logger.info("\n写入打卡数据到本地...")
        with local_engine.connect() as conn:
            for punch in punches:
                # 检查字段数量,兼容有无地理位置字段的情况
                if len(punch) >= 8:  # 包含地理位置字段
                    conn.execute(text("""
                        INSERT INTO punches 
                        (id, user_id, punch_date, punch_time, is_late_shift, created_at, latitude, longitude, location_name)
                        VALUES (:id, :user_id, :punch_date, :punch_time, :is_late_shift, :created_at, :latitude, :longitude, :location_name)
                    """), {
                        'id': punch[0],
                        'user_id': punch[1],
                        'punch_date': punch[2],
                        'punch_time': punch[3],
                        'is_late_shift': punch[4],
                        'created_at': punch[5],
                        'latitude': punch[6] if len(punch) > 6 else None,
                        'longitude': punch[7] if len(punch) > 7 else None,
                        'location_name': punch[8] if len(punch) > 8 else None
                    })
                else:  # 不包含地理位置字段
                    conn.execute(text("""
                        INSERT INTO punches 
                        (id, user_id, punch_date, punch_time, is_late_shift, created_at)
                        VALUES (:id, :user_id, :punch_date, :punch_time, :is_late_shift, :created_at)
                    """), {
                        'id': punch[0],
                        'user_id': punch[1],
                        'punch_date': punch[2],
                        'punch_time': punch[3],
                        'is_late_shift': punch[4],
                        'created_at': punch[5]
                    })
            conn.commit()
            logger.info(f"✓ 已写入 {len(punches)} 条打卡记录")
        
        # 验证同步结果
        logger.info("\n验证同步结果...")
        with local_engine.connect() as conn:
            user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            punch_count = conn.execute(text("SELECT COUNT(*) FROM punches")).scalar()
            logger.info(f"✓ 本地用户数: {user_count}")
            logger.info(f"✓ 本地打卡记录数: {punch_count}")
        
        logger.info("\n" + "="*50)
        logger.info("✅ 同步完成!")
        logger.info("="*50)
        logger.info(f"\n备份文件: {backup_name}")
        logger.info(f"用户数: {len(users)}")
        logger.info(f"打卡记录数: {len(punches)}")
        
    except Exception as e:
        logger.error(f"\n❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("="*50)
    print("Supabase → 本地SQLite 数据同步工具")
    print("="*50)
    print("\n⚠️  警告: 此操作将覆盖本地数据库!")
    print("本地数据将被备份到: punch_timer_backup_YYYYMMDD_HHMMSS.db")
    print()
    
    confirm = input("确认继续? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        sync_from_supabase_to_local()
    else:
        print("\n已取消同步")
