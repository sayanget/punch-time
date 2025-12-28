"""
数据迁移脚本 - 将JSON文件数据迁移到PostgreSQL数据库
使用方法: python migrate_to_db.py
"""
import json
import os
from datetime import datetime
from db_config import init_database
from db_models import create_user, add_punch, get_user_id_by_username
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JSON文件路径
USERS_FILE = 'users.json'
PUNCHES_FILE = 'punches.json'

def migrate_users():
    """迁移用户数据"""
    if not os.path.exists(USERS_FILE):
        logger.warning(f"{USERS_FILE} 不存在,跳过用户迁移")
        return {}
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    user_id_map = {}  # 用户名到数据库ID的映射
    
    for username, user_data in users.items():
        try:
            password_hash = user_data['password']
            user_id = create_user(username, password_hash)
            user_id_map[username] = user_id
            logger.info(f"迁移用户成功: {username} -> ID {user_id}")
        except Exception as e:
            logger.error(f"迁移用户失败 {username}: {e}")
            # 如果用户已存在,获取其ID
            user_id = get_user_id_by_username(username)
            if user_id:
                user_id_map[username] = user_id
                logger.info(f"用户已存在: {username} -> ID {user_id}")
    
    return user_id_map

def migrate_punches(user_id_map):
    """迁移打卡记录"""
    if not os.path.exists(PUNCHES_FILE):
        logger.warning(f"{PUNCHES_FILE} 不存在,跳过打卡记录迁移")
        return
    
    with open(PUNCHES_FILE, 'r', encoding='utf-8') as f:
        punches = json.load(f)
    
    total_count = 0
    success_count = 0
    
    for username, user_punches in punches.items():
        if username not in user_id_map:
            logger.warning(f"用户 {username} 不在映射表中,跳过其打卡记录")
            continue
        
        user_id = user_id_map[username]
        
        for date, times in user_punches.items():
            for punch_time in times:
                total_count += 1
                try:
                    # 检查是否为末班打卡(凌晨6点前)
                    dt = datetime.fromisoformat(punch_time)
                    is_late_shift = dt.hour < 6
                    
                    # 添加打卡记录
                    punch_id = add_punch(user_id, date, punch_time, is_late_shift)
                    if punch_id:
                        success_count += 1
                        logger.debug(f"迁移打卡记录成功: {username} - {punch_time}")
                except Exception as e:
                    logger.error(f"迁移打卡记录失败 {username} - {punch_time}: {e}")
    
    logger.info(f"打卡记录迁移完成: 总计 {total_count} 条, 成功 {success_count} 条")

def main():
    """主函数"""
    logger.info("开始数据迁移...")
    
    # 初始化数据库
    logger.info("初始化数据库...")
    init_database()
    
    # 迁移用户
    logger.info("迁移用户数据...")
    user_id_map = migrate_users()
    logger.info(f"用户迁移完成,共 {len(user_id_map)} 个用户")
    
    # 迁移打卡记录
    logger.info("迁移打卡记录...")
    migrate_punches(user_id_map)
    
    logger.info("数据迁移完成!")
    logger.info("提示: 迁移成功后,建议备份原JSON文件,然后可以删除它们")

if __name__ == '__main__':
    main()
