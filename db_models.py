"""
数据库模型和操作
提供用户和打卡记录的CRUD操作
"""
from sqlalchemy import text
from datetime import datetime, timedelta
from db_config import get_db
import logging

logger = logging.getLogger(__name__)

# ==================== 用户操作 ====================

def create_user(username, password_hash):
    """创建新用户"""
    db = get_db()
    try:
        result = db.execute(
            text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash) RETURNING id"),
            {"username": username, "password_hash": password_hash}
        )
        db.flush()  # flush确保语句执行完成
        user_id = result.fetchone()[0]  # 使用RETURNING获取ID,兼容PostgreSQL和SQLite
        db.commit()
        db.close()
        logger.info(f"创建用户成功: {username}")
        return user_id
    except Exception as e:
        db.rollback()
        db.close()
        logger.error(f"创建用户失败: {e}")
        raise

def get_user_by_username(username):
    """根据用户名获取用户信息"""
    db = get_db()
    try:
        result = db.execute(
            text("SELECT id, username, password_hash, created_at FROM users WHERE username = :username"),
            {"username": username}
        )
        user = result.fetchone()
        db.close()
        return user
    except Exception as e:
        db.close()
        logger.error(f"查询用户失败: {e}")
        return None

def user_exists(username):
    """检查用户是否存在"""
    user = get_user_by_username(username)
    return user is not None

def get_all_users():
    """获取所有用户(用于数据迁移)"""
    db = get_db()
    try:
        result = db.execute(text("SELECT id, username, password_hash, created_at FROM users"))
        users = result.fetchall()
        db.close()
        return users
    except Exception as e:
        db.close()
        logger.error(f"查询所有用户失败: {e}")
        return []

# ==================== 打卡记录操作 ====================

def add_punch(user_id, punch_date, punch_time, is_late_shift=False, latitude=None, longitude=None, location_name=None):
    """添加打卡记录（支持地理位置）"""
    db = get_db()
    try:
        # 检查是否已存在相同的打卡记录(同一用户、同一日期、同一时间)
        # 注意: 允许相同的punch_time在不同的punch_date存在(用于末班打卡)
        existing = db.execute(
            text("SELECT id FROM punches WHERE user_id = :user_id AND punch_date = :punch_date AND punch_time = :punch_time"),
            {"user_id": user_id, "punch_date": punch_date, "punch_time": punch_time}
        ).fetchone()
        
        if existing:
            db.close()
            logger.warning(f"打卡记录已存在: user_id={user_id}, punch_date={punch_date}, punch_time={punch_time}")
            return None
        
        # 插入新记录 - 使用RETURNING获取ID,兼容PostgreSQL和SQLite
        result = db.execute(
            text("""
                INSERT INTO punches (user_id, punch_date, punch_time, is_late_shift, latitude, longitude, location_name) 
                VALUES (:user_id, :punch_date, :punch_time, :is_late_shift, :latitude, :longitude, :location_name)
                RETURNING id
            """),
            {
                "user_id": user_id,
                "punch_date": punch_date,
                "punch_time": punch_time,
                "is_late_shift": is_late_shift,
                "latitude": latitude,
                "longitude": longitude,
                "location_name": location_name
            }
        )
        db.flush()  # flush确保语句执行完成
        punch_id = result.fetchone()[0]  # 使用RETURNING获取ID,兼容PostgreSQL和SQLite
        db.commit()
        db.close()
        logger.info(f"添加打卡记录成功: user_id={user_id}, punch_time={punch_time}")
        return punch_id
    except Exception as e:
        db.rollback()
        db.close()
        logger.error(f"添加打卡记录失败: {e}")
        raise

def get_user_punches(user_id):
    """获取用户的所有打卡记录,按日期分组（包含地理位置信息）"""
    db = get_db()
    has_location_fields = False
    punches = []
    
    try:
        # 首先检查表结构，确定是否有位置字段
        try:
            # 尝试查询包含位置信息的完整数据
            result = db.execute(
                text("""
                    SELECT punch_date, punch_time, is_late_shift, latitude, longitude, location_name
                    FROM punches 
                    WHERE user_id = :user_id 
                    ORDER BY punch_time
                """),
                {"user_id": user_id}
            )
            punches = result.fetchall()
            has_location_fields = True
            logger.info(f"使用新格式查询（包含位置字段），获取到 {len(punches)} 条记录")
        except Exception as e:
            # 如果查询失败（可能是因为字段不存在），回滚并使用旧查询
            logger.warning(f"查询位置字段失败: {str(e)[:100]}")
            logger.info("尝试使用旧格式查询（不包含位置字段）")
            
            # 关闭当前连接并重新获取
            try:
                db.rollback()
            except:
                pass
            
            db.close()
            db = get_db()
            
            # 使用旧查询格式
            result = db.execute(
                text("""
                    SELECT punch_date, punch_time, is_late_shift
                    FROM punches 
                    WHERE user_id = :user_id 
                    ORDER BY punch_time
                """),
                {"user_id": user_id}
            )
            punches = result.fetchall()
            has_location_fields = False
            logger.info(f"使用旧格式查询成功，获取到 {len(punches)} 条记录")
        
        # 按日期分组
        punches_by_date = {}
        for punch in punches:
            try:
                date_str = punch[0].strftime('%Y-%m-%d') if hasattr(punch[0], 'strftime') else str(punch[0])
                time_str = punch[1].isoformat() if hasattr(punch[1], 'isoformat') else str(punch[1])
                
                if date_str not in punches_by_date:
                    punches_by_date[date_str] = []
                
                # 构建打卡记录对象（包含位置信息，如果有的话）
                if has_location_fields:
                    punch_record = {
                        'time': time_str,
                        'latitude': punch[3] if len(punch) > 3 else None,
                        'longitude': punch[4] if len(punch) > 4 else None,
                        'location_name': punch[5] if len(punch) > 5 else None
                    }
                else:
                    # 向后兼容：旧数据没有位置信息
                    punch_record = {
                        'time': time_str,
                        'latitude': None,
                        'longitude': None,
                        'location_name': None
                    }
                punches_by_date[date_str].append(punch_record)
            except Exception as e:
                logger.error(f"处理打卡记录时出错: {e}, 记录: {punch}")
                continue
        
        db.close()
        logger.info(f"成功返回 {len(punches_by_date)} 个日期的打卡记录")
        return punches_by_date
        
    except Exception as e:
        logger.error(f"查询打卡记录失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        try:
            db.close()
        except:
            pass
        return {}

def get_punches_by_date(user_id, punch_date):
    """获取用户在指定日期的打卡记录"""
    db = get_db()
    try:
        result = db.execute(
            text("""
                SELECT punch_time 
                FROM punches 
                WHERE user_id = :user_id AND punch_date = :punch_date 
                ORDER BY punch_time
            """),
            {"user_id": user_id, "punch_date": punch_date}
        )
        punches = result.fetchall()
        result_list = [punch[0].isoformat() if hasattr(punch[0], 'isoformat') else str(punch[0]) for punch in punches]
        db.close()
        return result_list
    except Exception as e:
        db.close()
        logger.error(f"查询指定日期打卡记录失败: {e}")
        return []

def delete_punch(user_id, punch_time):
    """删除打卡记录"""
    db = get_db()
    try:
        result = db.execute(
            text("DELETE FROM punches WHERE user_id = :user_id AND punch_time = :punch_time"),
            {"user_id": user_id, "punch_time": punch_time}
        )
        db.commit()
        deleted_count = result.rowcount
        
        if deleted_count > 0:
            db.close()
            logger.info(f"删除打卡记录成功: user_id={user_id}, punch_time={punch_time}")
            return True
        else:
            db.close()
            logger.warning(f"未找到要删除的打卡记录: user_id={user_id}, punch_time={punch_time}")
            return False
    except Exception as e:
        db.rollback()
        db.close()
        logger.error(f"删除打卡记录失败: {e}")
        raise

def count_punches_by_date(user_id, punch_date):
    """统计用户在指定日期的打卡次数"""
    db = get_db()
    try:
        result = db.execute(
            text("SELECT COUNT(*) FROM punches WHERE user_id = :user_id AND punch_date = :punch_date"),
            {"user_id": user_id, "punch_date": punch_date}
        )
        count = result.fetchone()[0]
        db.close()
        return count
    except Exception as e:
        db.close()
        logger.error(f"统计打卡次数失败: {e}")
        return 0

def get_user_id_by_username(username):
    """根据用户名获取用户ID"""
    user = get_user_by_username(username)
    if user:
        return user[0]  # id是第一个字段
    return None
