# 打卡计时器 - 云端部署指南

本指南提供多种云平台的部署方案,帮助你将打卡计时器应用部署到云端运行。

## 目录

1. [准备工作](#准备工作)
2. [Docker部署(推荐)](#docker部署推荐)
3. [阿里云ECS部署](#阿里云ecs部署)
4. [腾讯云服务器部署](#腾讯云服务器部署)
5. [AWS EC2部署](#aws-ec2部署)
6. [Heroku部署](#heroku部署)
7. [Railway部署](#railway部署)
8. [Render部署](#render部署)
9. [安全配置](#安全配置)
10. [常见问题](#常见问题)

---

## 准备工作

### 1. 修改应用配置

在部署前,需要修改 `app.py` 中的配置:

```python
# 修改 secret_key (第9行)
app.secret_key = os.environ.get('SECRET_KEY', 'your-random-secret-key-here')

# 生产环境配置
if __name__ == '__main__':
    init_data_files()
    # 使用环境变量控制调试模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    port = int(os.environ.get('PORT', 7777))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

### 2. 创建生产环境依赖文件

创建 `requirements-prod.txt`:

```
Flask==3.0.3
Werkzeug==3.0.3
waitress==3.0.0
gunicorn==21.2.0
```

### 3. 数据持久化考虑

当前应用使用JSON文件存储数据。在云端部署时,建议:
- 使用云存储服务(如阿里云OSS、AWS S3)
- 或迁移到数据库(如PostgreSQL、MySQL)
- 或使用Docker卷挂载持久化数据

---

## Docker部署(推荐)

Docker是最推荐的部署方式,可以在任何支持Docker的云平台运行。

### 1. 创建Dockerfile

项目已包含 `Dockerfile`,内容如下:

```dockerfile
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

# 暴露端口
EXPOSE 7777

# 使用waitress作为生产服务器
CMD ["python", "-c", "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=7777)"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  punch-timer:
    build: .
    ports:
      - "7777:7777"
    volumes:
      - ./data:/app/data
    environment:
      - SECRET_KEY=your-secret-key-here
      - FLASK_DEBUG=False
    restart: unless-stopped
```

### 3. 构建和运行

```bash
# 构建镜像
docker build -t punch-timer .

# 运行容器
docker run -d -p 7777:7777 -v $(pwd)/data:/app/data --name punch-timer punch-timer

# 或使用docker-compose
docker-compose up -d
```

---

## 阿里云ECS部署

### 1. 购买ECS实例

- 选择Ubuntu 20.04或CentOS 7系统
- 配置:1核2GB即可(根据用户量调整)
- 开放安全组端口:7777、80、443

### 2. 连接服务器并安装环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip -y

# 安装Git
sudo apt install git -y
```

### 3. 部署应用

```bash
# 克隆或上传项目
git clone <your-repo-url>
cd punch_timer

# 安装依赖
pip3 install -r requirements.txt

# 使用waitress运行(生产环境)
python3 -c "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=7777)"
```

### 4. 使用systemd设置自动启动

创建 `/etc/systemd/system/punch-timer.service`:

```ini
[Unit]
Description=Punch Timer Web Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/punch_timer
ExecStart=/usr/bin/python3 -c "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=7777)"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable punch-timer
sudo systemctl start punch-timer
sudo systemctl status punch-timer
```

### 5. 配置Nginx反向代理(可选)

```bash
# 安装Nginx
sudo apt install nginx -y

# 创建配置文件
sudo nano /etc/nginx/sites-available/punch-timer
```

配置内容:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7777;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置:

```bash
sudo ln -s /etc/nginx/sites-available/punch-timer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 腾讯云服务器部署

腾讯云部署步骤与阿里云类似,主要区别:

1. 在腾讯云控制台购买云服务器CVM
2. 配置安全组规则,开放端口
3. 按照阿里云ECS的步骤2-5进行部署

---

## AWS EC2部署

### 1. 创建EC2实例

- 选择Amazon Linux 2或Ubuntu
- 实例类型:t2.micro(免费套餐)或更高
- 配置安全组:允许入站流量端口7777、80、443

### 2. 连接实例

```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

### 3. 部署应用

```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install python3 python3-pip git -y

# 或 Ubuntu
sudo apt update && sudo apt install python3 python3-pip git -y

# 克隆项目
git clone <your-repo-url>
cd punch_timer

# 安装依赖
pip3 install -r requirements.txt

# 运行应用
python3 -c "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=7777)"
```

### 4. 使用PM2管理进程(推荐)

```bash
# 安装Node.js和PM2
curl -sL https://rpm.nodesource.com/setup_16.x | sudo bash -
sudo yum install nodejs -y
sudo npm install -g pm2

# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
cd /home/ec2-user/punch_timer
python3 -c "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=7777)"
EOF

chmod +x start.sh

# 使用PM2启动
pm2 start start.sh --name punch-timer
pm2 save
pm2 startup
```

---

## Heroku部署

Heroku是一个简单易用的PaaS平台,适合快速部署。

### 1. 准备文件

创建 `Procfile`:

```
web: python -c "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=$PORT)"
```

创建 `runtime.txt`:

```
python-3.11.0
```

### 2. 部署步骤

```bash
# 安装Heroku CLI
# 访问 https://devcenter.heroku.com/articles/heroku-cli

# 登录Heroku
heroku login

# 创建应用
heroku create your-app-name

# 设置环境变量
heroku config:set SECRET_KEY=your-secret-key

# 部署
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 查看日志
heroku logs --tail
```

**注意**: Heroku的免费套餐文件系统是临时的,重启后数据会丢失。建议使用Heroku Postgres插件存储数据。

---

## Railway部署

Railway是一个现代化的部署平台,支持自动部署。

### 1. 准备配置

创建 `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python -c \"from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=$PORT)\"",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. 部署步骤

1. 访问 https://railway.app
2. 使用GitHub账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择你的仓库
5. 设置环境变量 `SECRET_KEY`
6. Railway会自动检测Python项目并部署

---

## Render部署

Render是另一个优秀的部署平台,提供免费套餐。

### 1. 准备配置

创建 `render.yaml`:

```yaml
services:
  - type: web
    name: punch-timer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -c "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=$PORT)"
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_DEBUG
        value: False
```

### 2. 部署步骤

1. 访问 https://render.com
2. 注册并连接GitHub
3. 点击 "New" → "Web Service"
4. 选择你的仓库
5. Render会自动检测配置并部署

---

## 安全配置

### 1. 环境变量管理

不要在代码中硬编码敏感信息,使用环境变量:

```python
import os

app.secret_key = os.environ.get('SECRET_KEY', 'fallback-key-for-dev')
```

### 2. HTTPS配置

使用Let's Encrypt免费SSL证书:

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com
```

### 3. 防火墙配置

```bash
# Ubuntu UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 4. 数据备份

定期备份数据文件:

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz users.json punches.json
# 上传到云存储(可选)
EOF

chmod +x backup.sh

# 添加到crontab(每天凌晨2点备份)
crontab -e
# 添加: 0 2 * * * /path/to/backup.sh
```

---

## 常见问题

### Q1: 如何修改端口?

修改 `app.py` 最后一行或使用环境变量 `PORT`。

### Q2: 数据会丢失吗?

使用Docker卷挂载或云存储可以持久化数据。

### Q3: 如何支持更多用户?

- 升级服务器配置
- 使用Nginx负载均衡
- 迁移到数据库存储

### Q4: 如何监控应用状态?

- 使用PM2: `pm2 monit`
- 使用systemd: `journalctl -u punch-timer -f`
- 云平台自带监控工具

### Q5: 如何更新应用?

```bash
# 拉取最新代码
git pull

# 重启服务
sudo systemctl restart punch-timer
# 或
pm2 restart punch-timer
# 或
docker-compose down && docker-compose up -d
```

---

## 推荐方案总结

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 个人使用 | Railway/Render | 免费、简单、自动部署 |
| 小团队 | 阿里云ECS + Docker | 稳定、可控、价格合理 |
| 企业使用 | AWS EC2 + RDS | 高可用、可扩展、专业支持 |
| 快速测试 | Heroku | 部署最快、配置简单 |
| 最佳实践 | Docker + 任意云平台 | 标准化、可移植、易维护 |

---

## 下一步

1. 选择适合的云平台
2. 按照对应章节部署
3. 配置域名和HTTPS
4. 设置数据备份
5. 监控应用运行状态

如有问题,请查看各云平台的官方文档或提交Issue。
