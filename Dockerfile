FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY app.py .
COPY config.py .
COPY templates/ templates/
COPY static/ static/

# 创建数据目录
RUN mkdir -p /app/data

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 7777

# 使用waitress作为生产服务器
CMD ["python", "-c", "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=7777)"]
