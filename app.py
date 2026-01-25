from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from datetime import datetime, timedelta
from functools import wraps

# 导入数据库模块
from db_config import init_database, close_db
from db_models import (
    create_user, get_user_by_username, user_exists, get_user_id_by_username,
    add_punch, get_user_punches, get_punches_by_date, delete_punch, count_punches_by_date,
    get_user_hourly_rate, set_user_hourly_rate
)

app = Flask(__name__, template_folder='templates', static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret_key_here')  # 使用环境变量

# 初始化数据库
init_database()

# 初始化日志
logger = logging.getLogger(__name__)


# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 首页 - 打卡页面
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# 用户注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 检查用户名是否已存在
        if user_exists(username):
            flash('用户名已存在')
            return redirect(url_for('register'))
        
        # 创建新用户
        hashed_password = generate_password_hash(password)
        try:
            create_user(username, hashed_password)
            flash('注册成功，请登录')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'注册失败: {str(e)}')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# 用户登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 验证用户
        user = get_user_by_username(username)
        if user and check_password_hash(user[2], password):  # user[2] is password_hash
            session['user_id'] = username
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

# 用户登出
@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# 获取当前用户信息
@app.route('/api/current-user')
@login_required
def current_user():
    return jsonify({'username': session['user_id']})

# 获取API配置（用于前端）
@app.route('/api/config')
@login_required
def get_config():
    return jsonify({
        'googleMapsApiKey': os.environ.get('GOOGLE_MAPS_API_KEY', '')
    })


# 获取当前用户的打卡数据
@app.route('/api/punches')
@login_required
def get_punches():
    username = session['user_id']
    user_id = get_user_id_by_username(username)
    if user_id:
        user_punches = get_user_punches(user_id)
        return jsonify(user_punches)
    return jsonify({})

# 添加打卡记录（支持末班打卡双记录显示和地理位置）
@app.route('/api/punch', methods=['POST'])
@login_required
def add_punch_route():
    data = request.get_json()
    date = data['date']
    time = data['time']
    is_late_shift_manual = data.get('lateShift', False)  # 是否为末班打卡（手动标记）
    
    # 获取地理位置数据（可选）
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    location_name = data.get('locationName')
    
    username = session['user_id']
    user_id = get_user_id_by_username(username)
    
    if not user_id:
        return jsonify({'success': False, 'message': '用户不存在'})
    
    # 只保留时分,去掉秒(HH:MM格式)
    time_parts = time.split(':')
    time_hhmm = f"{time_parts[0]}:{time_parts[1]}"
    
    # 添加打卡时间(只精确到分钟)
    punch_time = f"{date}T{time_hhmm}"
    
    # 自动判断是否为末班打卡（时间在早上5点前）
    hour = int(time_parts[0])
    is_late_shift_auto = hour < 5  # 早上5点前的打卡自动标记为末班打卡
    is_late_shift = is_late_shift_manual or is_late_shift_auto
    
    try:
        # 添加到当前日期（包含地理位置信息）
        punch_id = add_punch(user_id, date, punch_time, is_late_shift, latitude, longitude, location_name)
        
        if punch_id is None:
            return jsonify({'success': False, 'message': '该时间已打卡'})
        
        # 如果是末班打卡，同时添加到前一天的记录中
        if is_late_shift:
            current_date = datetime.strptime(date, '%Y-%m-%d')
            previous_date = current_date - timedelta(days=1)
            previous_date_str = previous_date.strftime('%Y-%m-%d')
            
            # 添加到前一天的记录中（同样包含地理位置信息）
            add_punch(user_id, previous_date_str, punch_time, is_late_shift, latitude, longitude, location_name)
        
        # 统计当天打卡次数
        count = count_punches_by_date(user_id, date)
        
        # 根据是否为末班打卡显示不同的消息
        if is_late_shift:
            return jsonify({'success': True, 'message': f'已记录第 {count} 次打卡（末班）'})
        else:
            return jsonify({'success': True, 'message': f'已记录第 {count} 次打卡'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'打卡失败: {str(e)}'})

# 删除打卡记录
@app.route('/api/punch/<date>/<path:timestamp>', methods=['DELETE'])
@login_required
def delete_punch_route(date, timestamp):
    username = session['user_id']
    user_id = get_user_id_by_username(username)
    
    if not user_id:
        return jsonify({'success': False, 'message': '用户不存在'})
    
    try:
        # 删除打卡记录
        success = delete_punch(user_id, timestamp)
        
        if success:
            # 检查是否为末班打卡(凌晨5点前的记录)
            # 如果是,也需要从前一天的记录中删除
            try:
                punch_dt = datetime.fromisoformat(timestamp)
                if punch_dt.hour < 5:  # 凌晨5点前的记录
                    # 计算前一天的日期
                    current_date = datetime.strptime(date, '%Y-%m-%d')
                    previous_date = current_date - timedelta(days=1)
                    previous_date_str = previous_date.strftime('%Y-%m-%d')
                    
                    # 从前一天的记录中也删除
                    delete_punch(user_id, timestamp)
            except Exception as e:
                # 如果处理双记录失败,记录错误但不影响主删除操作
                print(f"处理双记录时出错: {str(e)}")
            
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '未找到该打卡记录'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

# 时薪管理API
@app.route('/api/hourly-rate', methods=['GET', 'POST'])
@login_required
def hourly_rate():
    """获取或设置用户时薪"""
    username = session['user_id']
    user_id = get_user_id_by_username(username)
    
    if not user_id:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    if request.method == 'GET':
        # 获取时薪
        try:
            rate = get_user_hourly_rate(user_id)
            return jsonify({'success': True, 'hourly_rate': rate})
        except Exception as e:
            logger.error(f"获取时薪失败: {e}")
            return jsonify({'success': False, 'message': f'获取时薪失败: {str(e)}'}), 500
    
    elif request.method == 'POST':
        # 设置时薪
        try:
            data = request.get_json()
            rate = float(data.get('hourly_rate', 0))
            
            if rate < 0:
                return jsonify({'success': False, 'message': '时薪不能为负数'}), 400
            
            set_user_hourly_rate(user_id, rate)
            return jsonify({'success': True, 'message': '时薪设置成功', 'hourly_rate': rate})
        except ValueError:
            return jsonify({'success': False, 'message': '时薪格式不正确'}), 400
        except Exception as e:
            logger.error(f"设置时薪失败: {e}")
            return jsonify({'success': False, 'message': f'设置时薪失败: {str(e)}'}), 500

# 工资汇总API
@app.route('/api/salary-summary', methods=['POST'])
@login_required
def salary_summary():
    """计算指定时间段的工资汇总"""
    try:
        username = session['user_id']
        user_id = get_user_id_by_username(username)
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'message': '请提供开始日期和结束日期'}), 400
        
        # 获取时薪
        hourly_rate = get_user_hourly_rate(user_id)
        
        # 获取所有打卡记录
        all_punches = get_user_punches(user_id)
        
        # 过滤指定时间段的记录
        total_hours = 0.0
        total_days = 0
        daily_details = []
        
        for date_str, records in sorted(all_punches.items()):
            if start_date <= date_str <= end_date:
                # 提取时间
                times = []
                for record in records:
                    if isinstance(record, dict):
                        time_str = record.get('time')
                        if time_str:
                            times.append(time_str)
                    elif isinstance(record, str):
                        times.append(record)
                
                # 计算当日工作时长
                if len(times) >= 4:
                    try:
                        # 如果打卡次数大于4次，只取最后4次
                        calc_times = times[-4:]
                        
                        from datetime import datetime
                        t1 = datetime.fromisoformat(calc_times[0])
                        t2 = datetime.fromisoformat(calc_times[1])
                        t3 = datetime.fromisoformat(calc_times[2])
                        t4 = datetime.fromisoformat(calc_times[3])
                        
                        morning_hours = (t2 - t1).total_seconds() / 3600
                        afternoon_hours = (t4 - t3).total_seconds() / 3600
                        day_hours = morning_hours + afternoon_hours
                        day_salary = day_hours * hourly_rate
                        
                        total_hours += day_hours
                        total_days += 1
                        
                        daily_details.append({
                            'date': date_str,
                            'hours': round(day_hours, 2),
                            'salary': round(day_salary, 2)
                        })
                    except Exception as e:
                        logger.warning(f"计算日期 {date_str} 工时失败: {e}")
                        continue
        
        total_salary = total_hours * hourly_rate
        
        return jsonify({
            'success': True,
            'summary': {
                'start_date': start_date,
                'end_date': end_date,
                'total_days': total_days,
                'total_hours': round(total_hours, 2),
                'hourly_rate': hourly_rate,
                'total_salary': round(total_salary, 2),
                'daily_details': daily_details
            }
        })
        
    except Exception as e:
        logger.error(f"工资汇总失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'工资汇总失败: {str(e)}'}), 500

# 导出个人打卡数据
@app.route('/api/export')
@login_required
def export_punches():
    """导出用户打卡数据为CSV文件"""
    try:
        logger.info("=== 开始导出流程 ===")
        
        # 1. 获取用户信息
        username = session.get('user_id')
        logger.info(f"当前用户: {username}")
        
        if not username:
            logger.error("Session中没有user_id")
            return jsonify({'success': False, 'message': 'Session无效'}), 401
        
        user_id = get_user_id_by_username(username)
        logger.info(f"用户ID: {user_id}")
        
        if not user_id:
            logger.error(f"找不到用户: {username}")
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 2. 获取打卡数据
        logger.info("获取打卡数据...")
        user_punches = get_user_punches(user_id)
        logger.info(f"获取到 {len(user_punches)} 天的打卡记录")
        
        # 3. 构建CSV
        logger.info("构建CSV数据...")
        csv_lines = []
        
        # UTF-8 BOM + 表头
        csv_lines.append("\ufeff日期,第1次,第2次,第3次,第4次,上午时长,下午时长,总时长")
        
        # 处理每一天的数据
        processed_late_shifts = set()
        
        for date in sorted(user_punches.keys()):
            try:
                logger.info(f"处理日期: {date}")
                records = user_punches[date]
                logger.info(f"  记录数: {len(records)}, 类型: {type(records)}")
                
                # 提取时间字符串
                times = []
                for i, record in enumerate(records):
                    try:
                        # 处理字典格式或字符串格式
                        if isinstance(record, dict):
                            time_str = record.get('time')
                            if not time_str:
                                logger.warning(f"  记录{i}的time为空: {record}")
                                continue
                        elif isinstance(record, str):
                            time_str = record
                        else:
                            logger.warning(f"  记录{i}类型未知: {type(record)}")
                            continue
                        
                        # 检查末班打卡（凌晨5点前）
                        try:
                            dt = datetime.fromisoformat(time_str)
                            if dt.hour < 5:
                                if time_str in processed_late_shifts:
                                    logger.info(f"  跳过重复末班打卡: {time_str}")
                                    continue
                                processed_late_shifts.add(time_str)
                        except Exception as e:
                            logger.warning(f"  解析时间失败: {time_str}, {e}")
                        
                        times.append(time_str)
                    except Exception as e:
                        logger.error(f"  处理记录{i}时出错: {e}")
                        continue
                
                logger.info(f"  有效时间数: {len(times)}")
                
                # 最多取4个时间 (取最后4次)
                if len(times) > 4:
                    times = times[-4:]
                else:
                    times = times[:4]
                
                # 格式化时间
                formatted_times = []
                for t in times:
                    try:
                        dt = datetime.fromisoformat(t)
                        formatted_times.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                    except:
                        formatted_times.append(str(t))
                
                # 计算时长
                morning_dur = ""
                afternoon_dur = ""
                total_dur = ""
                
                if len(times) >= 4:
                    try:
                        t1 = datetime.fromisoformat(times[0])
                        t2 = datetime.fromisoformat(times[1])
                        t3 = datetime.fromisoformat(times[2])
                        t4 = datetime.fromisoformat(times[3])
                        
                        morning_sec = (t2 - t1).total_seconds()
                        afternoon_sec = (t4 - t3).total_seconds()
                        total_sec = morning_sec + afternoon_sec
                        
                        morning_dur = f"{int(morning_sec//3600)}小时{int((morning_sec%3600)//60)}分钟"
                        afternoon_dur = f"{int(afternoon_sec//3600)}小时{int((afternoon_sec%3600)//60)}分钟"
                        total_dur = f"{int(total_sec//3600)}小时{int((total_sec%3600)//60)}分钟"
                    except Exception as e:
                        logger.warning(f"  计算时长失败: {e}")
                
                # 填充到4列
                while len(formatted_times) < 4:
                    formatted_times.append("")
                
                # 构建行
                row = [date] + formatted_times + [morning_dur, afternoon_dur, total_dur]
                csv_lines.append(",".join(row))
                
            except Exception as e:
                logger.error(f"处理日期{date}时出错: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        # 4. 生成响应
        logger.info(f"CSV总行数: {len(csv_lines)}")
        csv_data = "\n".join(csv_lines)
        
        response = app.response_class(
            response=csv_data,
            status=200,
            mimetype='text/csv; charset=utf-8'
        )
        response.headers['Content-Disposition'] = 'attachment; filename=punches.csv'
        
        logger.info("=== 导出成功 ===")
        return response
        
    except Exception as e:
        logger.error(f"!!! 导出失败 !!!")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        import traceback
        logger.error(f"完整堆栈:\n{traceback.format_exc()}")
        
        # 返回JSON错误响应
        return jsonify({
            'success': False,
            'message': f'导出失败: {str(e)}',
            'error_type': type(e).__name__
        }), 500

# 为静态文件提供路由
@app.route('/index.html')
def index_html():
    return render_template('index.html')

if __name__ == '__main__':
    # 检查是否启用SSL
    ssl_enabled = os.environ.get('SSL_ENABLED', 'False').lower() == 'true'
    
    if ssl_enabled:
        # 使用HTTPS
        ssl_cert = os.environ.get('SSL_CERT_PATH', 'ssl/cert.pem')
        ssl_key = os.environ.get('SSL_KEY_PATH', 'ssl/key.pem')
        port = int(os.environ.get('HTTPS_PORT', '7778'))
        
        # 检查证书文件是否存在
        if not os.path.exists(ssl_cert) or not os.path.exists(ssl_key):
            print(f"错误: SSL证书文件不存在!")
            print(f"  证书: {ssl_cert}")
            print(f"  私钥: {ssl_key}")
            print(f"\n请先运行: python generate_ssl_cert.py")
            exit(1)
        
        print(f"启动HTTPS服务器...")
        print(f"访问地址: https://localhost:{port}")
        app.run(debug=True, host='0.0.0.0', port=port, ssl_context=(ssl_cert, ssl_key))
    else:
        # 使用HTTP
        port = int(os.environ.get('PORT', '7777'))
        print(f"启动HTTP服务器...")
        print(f"访问地址: http://localhost:{port}")
        app.run(debug=True, host='0.0.0.0', port=port)
