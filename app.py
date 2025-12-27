from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='.', static_url_path='')
app.secret_key = 'your-secret_key_here'  # 在生产环境中应该使用环境变量

# 数据文件路径
USERS_FILE = 'users.json'
PUNCHES_FILE = 'punches.json'

# 确保数据文件存在
def init_data_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    if not os.path.exists(PUNCHES_FILE):
        with open(PUNCHES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
init_data_files()

# 加载用户数据
def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存用户数据
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# 加载打卡数据
def load_punches():
    with open(PUNCHES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存打卡数据
def save_punches(punches):
    with open(PUNCHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(punches, f, ensure_ascii=False, indent=2)

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
        users = load_users()
        if username in users:
            flash('用户名已存在')
            return redirect(url_for('register'))
        
        # 创建新用户
        hashed_password = generate_password_hash(password)
        users[username] = {
            'password': hashed_password,
            'created_at': datetime.now().isoformat()
        }
        save_users(users)
        
        flash('注册成功，请登录')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# 用户登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 验证用户
        users = load_users()
        if username in users and check_password_hash(users[username]['password'], password):
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

# 获取当前用户的打卡数据
@app.route('/api/punches')
@login_required
def get_punches():
    punches = load_punches()
    user_punches = punches.get(session['user_id'], {})
    return jsonify(user_punches)

# 添加打卡记录（支持末班打卡双记录显示）
@app.route('/api/punch', methods=['POST'])
@login_required
def add_punch():
    data = request.get_json()
    date = data['date']
    time = data['time']
    is_late_shift_manual = data.get('lateShift', False)  # 是否为末班打卡（手动标记）
    
    punches = load_punches()
    user_id = session['user_id']
    
    # 如果用户还没有打卡记录，初始化
    if user_id not in punches:
        punches[user_id] = {}
    
    # 如果日期还没有打卡记录，初始化
    if date not in punches[user_id]:
        punches[user_id][date] = []
    
    # 添加打卡时间
    punch_time = f"{date}T{time}"
    
    # 检查是否已打卡
    if punch_time not in punches[user_id][date]:
        # 添加到指定日期
        punches[user_id][date].append(punch_time)
        punches[user_id][date].sort()
        
        # 自动判断是否为末班打卡（时间在早上6点前）
        time_parts = time.split(':')
        hour = int(time_parts[0])
        is_late_shift_auto = hour < 6  # 早上6点前的打卡自动标记为末班打卡
        
        # 如果手动标记为末班打卡或自动判断为末班打卡，则同时添加到前一天的记录中
        if is_late_shift_manual or is_late_shift_auto:
            from datetime import datetime, timedelta
            current_date = datetime.strptime(date, '%Y-%m-%d')
            previous_date = current_date - timedelta(days=1)
            previous_date_str = previous_date.strftime('%Y-%m-%d')
            
            # 初始化前一天的记录
            if previous_date_str not in punches[user_id]:
                punches[user_id][previous_date_str] = []
            
            # 添加到前一天的记录中（如果该时间尚未存在于前一天的记录中）
            if punch_time not in punches[user_id][previous_date_str]:
                punches[user_id][previous_date_str].append(punch_time)
                punches[user_id][previous_date_str].sort()
        
        # 限制每天最多4次打卡
        if len(punches[user_id][date]) > 4:
            punches[user_id][date] = punches[user_id][date][:4]
        
        save_punches(punches)
        
        # 根据是否为末班打卡显示不同的消息
        if is_late_shift_manual or is_late_shift_auto:
            return jsonify({'success': True, 'message': f'已记录第 {len(punches[user_id][date])} 次打卡（末班）'})
        else:
            return jsonify({'success': True, 'message': f'已记录第 {len(punches[user_id][date])} 次打卡'})
    else:
        return jsonify({'success': False, 'message': '该时间已打卡'})

# 删除打卡记录
@app.route('/api/punch/<date>/<index>', methods=['DELETE'])
@login_required
def delete_punch(date, index):
    punches = load_punches()
    user_id = session['user_id']
    
    if user_id in punches and date in punches[user_id]:
        try:
            index = int(index)
            if 0 <= index < len(punches[user_id][date]):
                punches[user_id][date].pop(index)
                if not punches[user_id][date]:  # 如果日期下没有打卡记录了，删除该日期
                    del punches[user_id][date]
                save_punches(punches)
                return jsonify({'success': True, 'message': '删除成功'})
        except (ValueError, IndexError):
            pass
    
    return jsonify({'success': False, 'message': '删除失败'})

# 导出个人打卡数据
@app.route('/api/export')
@login_required
def export_punches():
    punches = load_punches()
    user_punches = punches.get(session['user_id'], {})
    
    # 准备CSV数据
    csv_data = "日期,第1次,第2次,第3次,第4次\n"
    for date, times in user_punches.items():
        # 确保最多只取4个时间
        formatted_times = times[:4] if len(times) >= 4 else times
        row = [date] + formatted_times
        csv_data += ",".join(row) + "\n"
    
    # 设置响应头以触发下载
    response = app.response_class(
        response=csv_data,
        status=200,
        mimetype='text/csv'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=punches.csv'
    return response

# 为静态文件提供路由
@app.route('/index.html')
def index_html():
    return render_template('index.html')

if __name__ == '__main__':    
    app.run(debug=True, host='0.0.0.0', port=7777)
