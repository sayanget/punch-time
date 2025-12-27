#!/bin/bash

# 打卡计时器 - 一键部署脚本 (适用于Ubuntu/Debian)
# 使用方法: sudo bash deploy.sh

set -e

echo "========================================="
echo "打卡计时器 - 云端部署脚本"
echo "========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 更新系统
echo "正在更新系统..."
apt update && apt upgrade -y

# 安装依赖
echo "正在安装依赖..."
apt install -y python3 python3-pip git nginx certbot python3-certbot-nginx

# 获取项目路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 安装Python依赖
echo "正在安装Python依赖..."
pip3 install -r requirements.txt

# 创建systemd服务
echo "正在创建systemd服务..."
cat > /etc/systemd/system/punch-timer.service << EOF
[Unit]
Description=Punch Timer Web Application
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="SECRET_KEY=$(openssl rand -hex 32)"
Environment="FLASK_DEBUG=False"
ExecStart=/usr/bin/python3 -c "from waitress import serve; from app import app, init_data_files; init_data_files(); serve(app, host='0.0.0.0', port=7777)"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
echo "正在启动服务..."
systemctl daemon-reload
systemctl enable punch-timer
systemctl start punch-timer

# 检查服务状态
sleep 2
if systemctl is-active --quiet punch-timer; then
    echo "✓ 服务启动成功"
else
    echo "✗ 服务启动失败，请检查日志: journalctl -u punch-timer -n 50"
    exit 1
fi

# 配置防火墙
echo "正在配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 7777/tcp
    echo "✓ 防火墙配置完成"
fi

# 询问是否配置Nginx
read -p "是否配置Nginx反向代理? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入域名 (例如: example.com): " DOMAIN
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/punch-timer << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:7777;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # 启用配置
    ln -sf /etc/nginx/sites-available/punch-timer /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    
    echo "✓ Nginx配置完成"
    
    # 询问是否配置SSL
    read -p "是否配置SSL证书 (Let's Encrypt)? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        certbot --nginx -d $DOMAIN
        echo "✓ SSL证书配置完成"
    fi
fi

echo ""
echo "========================================="
echo "部署完成!"
echo "========================================="
echo "应用已在以下地址运行:"
echo "  - http://localhost:7777"
if [ ! -z "$DOMAIN" ]; then
    echo "  - http://$DOMAIN"
fi
echo ""
echo "服务管理命令:"
echo "  启动: sudo systemctl start punch-timer"
echo "  停止: sudo systemctl stop punch-timer"
echo "  重启: sudo systemctl restart punch-timer"
echo "  状态: sudo systemctl status punch-timer"
echo "  日志: sudo journalctl -u punch-timer -f"
echo "========================================="
