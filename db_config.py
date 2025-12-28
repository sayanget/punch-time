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

def close_db(db=None):
    """关闭数据库连接"""
    if db:
        db.close()

