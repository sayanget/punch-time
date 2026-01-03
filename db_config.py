"""
数据库配置和连接管理
支持PostgreSQL和SQLite(本地开发)
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量获取数据库URL
# 如果未设置,使用SQLite作为本地开发数据库
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///punch_timer.db')

# 修复Heroku/Render的postgres://协议问题(需要postgresql://)
# 同时指定使用psycopg3驱动
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
elif DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)

# 创建数据库引擎
# 对于SQLite使用check_same_thread=False
# 对于PostgreSQL使用连接池
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL,
        connect_args={'check_same_thread': False},
        echo=False
    )
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Render等平台推荐使用NullPool
        echo=False
    )

# 创建Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        db.close()
        raise

def init_database():
    """初始化数据库表结构"""
    try:
        with engine.connect() as conn:
            # 创建users表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 创建punches表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS punches (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    punch_date DATE NOT NULL,
                    punch_time TIMESTAMP NOT NULL,
                    is_late_shift BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, punch_time),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            # 创建索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_punches_user_date 
                ON punches(user_id, punch_date)
            """))
            
            conn.commit()
            logger.info("数据库表初始化成功")
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        # 对于SQLite,使用不同的语法
        if DATABASE_URL.startswith('sqlite'):
            try:
                with engine.connect() as conn:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username VARCHAR(50) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS punches (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            punch_date DATE NOT NULL,
                            punch_time TIMESTAMP NOT NULL,
                            is_late_shift BOOLEAN DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, punch_time),
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                    """))
                    
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_punches_user_date 
                        ON punches(user_id, punch_date)
                    """))
                    
                    conn.commit()
                    logger.info("SQLite数据库表初始化成功")
            except Exception as sqlite_error:
                logger.error(f"SQLite初始化失败: {sqlite_error}")
                raise
    
    # 修复唯一约束问题(PostgreSQL)
    if not DATABASE_URL.startswith('sqlite'):
        try:
            logger.info("检查并修复数据库唯一约束...")
            with engine.connect() as conn:
                # 检查是否存在旧的约束
                result = conn.execute(text("""
                    SELECT conname 
                    FROM pg_constraint 
                    WHERE conrelid = 'punches'::regclass 
                    AND contype = 'u'
                    AND conname = 'punches_user_id_punch_time_key'
                """))
                old_constraint = result.fetchone()
                
                if old_constraint:
                    logger.info("发现旧约束,正在删除...")
                    # 删除旧约束
                    conn.execute(text("ALTER TABLE punches DROP CONSTRAINT IF EXISTS punches_user_id_punch_time_key"))
                    conn.commit()
                    logger.info("✓ 已删除旧约束: punches_user_id_punch_time_key")
                
                # 检查是否存在新约束
                result = conn.execute(text("""
                    SELECT conname 
                    FROM pg_constraint 
                    WHERE conrelid = 'punches'::regclass 
                    AND contype = 'u'
                    AND conname = 'punches_user_id_punch_date_punch_time_key'
                """))
                new_constraint = result.fetchone()
                
                if not new_constraint:
                    logger.info("添加新约束...")
                    # 添加新约束
                    conn.execute(text("""
                        ALTER TABLE punches 
                        ADD CONSTRAINT punches_user_id_punch_date_punch_time_key 
                        UNIQUE (user_id, punch_date, punch_time)
                    """))
                    conn.commit()
                    logger.info("✓ 已添加新约束: punches_user_id_punch_date_punch_time_key")
                else:
                    logger.info("✓ 新约束已存在,无需修复")
                    
        except Exception as e:
            logger.warning(f"约束修复失败(可能已经修复): {e}")

def close_db(db=None):
    """关闭数据库连接"""
    if db:
        db.close()

