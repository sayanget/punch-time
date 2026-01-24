"""
数据库迁移脚本：添加hourly_rate字段到users表
"""
from sqlalchemy import text
from db_config import get_db, DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """添加hourly_rate字段到users表"""
    logger.info(f"数据库: {DATABASE_URL}")
    logger.info("开始迁移...")
    
    try:
        db = get_db()
        
        # 检查字段是否已存在
        if DATABASE_URL.startswith('sqlite'):
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
        else:
            # PostgreSQL
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
            """))
            columns = [row[0] for row in result.fetchall()]
        
        if 'hourly_rate' in columns:
            logger.info("✓ hourly_rate字段已存在，跳过迁移")
            db.close()
            return
        
        # 添加hourly_rate字段
        logger.info("添加hourly_rate字段...")
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN hourly_rate DECIMAL(10, 2) DEFAULT 0.00
        """))
        
        db.commit()
        logger.info("✓ 迁移成功完成")
        
        # 验证
        if DATABASE_URL.startswith('sqlite'):
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
        else:
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
            """))
            columns = [row[0] for row in result.fetchall()]
        
        logger.info(f"✓ 当前users表字段: {', '.join(columns)}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    migrate()
