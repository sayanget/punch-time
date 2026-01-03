"""
数据库迁移脚本 - 自动修复唯一约束
在Render部署时自动执行
"""
import os
import sys
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """执行数据库迁移"""
    # 获取数据库URL
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL环境变量未设置")
        return False
    
    # 修复Render的postgres://协议问题
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    try:
        # 创建数据库引擎
        engine = create_engine(database_url, echo=True)
        
        logger.info("开始数据库迁移...")
        
        with engine.connect() as conn:
            # 步骤1: 检查当前约束
            logger.info("检查当前约束...")
            result = conn.execute(text("""
                SELECT conname 
                FROM pg_constraint 
                WHERE conrelid = 'punches'::regclass 
                AND contype = 'u'
                AND conname LIKE '%punch_time%'
            """))
            constraints = [row[0] for row in result.fetchall()]
            logger.info(f"找到约束: {constraints}")
            
            # 步骤2: 删除旧的唯一约束
            if constraints:
                for constraint_name in constraints:
                    logger.info(f"删除旧约束: {constraint_name}")
                    conn.execute(text(f"ALTER TABLE punches DROP CONSTRAINT IF EXISTS {constraint_name}"))
                    conn.commit()
                    logger.info(f"✓ 已删除约束: {constraint_name}")
            
            # 步骤3: 添加新的唯一约束
            logger.info("添加新的唯一约束...")
            conn.execute(text("""
                ALTER TABLE punches 
                ADD CONSTRAINT punches_user_id_punch_date_punch_time_key 
                UNIQUE (user_id, punch_date, punch_time)
            """))
            conn.commit()
            logger.info("✓ 已添加新约束: punches_user_id_punch_date_punch_time_key")
            
            # 步骤4: 验证新约束
            logger.info("验证新约束...")
            result = conn.execute(text("""
                SELECT conname 
                FROM pg_constraint 
                WHERE conrelid = 'punches'::regclass 
                AND contype = 'u'
            """))
            new_constraints = [row[0] for row in result.fetchall()]
            logger.info(f"当前约束: {new_constraints}")
            
            if 'punches_user_id_punch_date_punch_time_key' in new_constraints:
                logger.info("✓ 数据库迁移成功!")
                return True
            else:
                logger.error("✗ 新约束未创建成功")
                return False
                
    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
