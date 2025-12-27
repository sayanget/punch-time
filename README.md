# 打卡计时器 (Punch Timer)

一个功能完整的多用户打卡系统,支持Web界面操作和多种运行模式。

## ✨ 主要功能

- **多用户系统** - 用户注册、登录,独立的打卡记录
- **打卡功能** - 每日4次打卡,支持手动时间输入和末班打卡
- **时间计算** - 自动计算各时段间隔时间和当前班次时长
- **数据管理** - 打卡记录删除、CSV导出、历史记录查看
- **多语言支持** - 中文、英文、西班牙文切换
- **移动端适配** - 响应式设计,适配各种屏幕尺寸
- **离线功能** - 支持离线数据录入和自动同步

## 🚀 快速开始

### 在线演示

访问部署的应用: [即将部署到Render]

### 本地运行

```bash
# 克隆项目
git clone https://github.com/yourusername/punch-timer.git
cd punch-timer

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

访问 http://localhost:7777

## 📦 部署

### Render部署(推荐)

1. Fork本仓库
2. 在 [Render](https://render.com) 创建新的Web Service
3. 连接你的GitHub仓库
4. Render会自动检测配置并部署

### Docker部署

```bash
# 使用Docker Compose
docker-compose up -d

# 或使用Docker
docker build -t punch-timer .
docker run -d -p 7777:7777 punch-timer
```

### 其他平台

支持部署到:
- Heroku
- Railway
- AWS EC2
- 阿里云ECS
- 腾讯云服务器

详见 [云端部署指南](CLOUD_DEPLOYMENT_GUIDE.md)

## 🛠️ 技术栈

- **后端**: Flask (Python 3.11)
- **前端**: HTML, CSS, JavaScript
- **数据存储**: JSON文件 (可扩展到数据库)
- **生产服务器**: Waitress WSGI

## 📖 文档

- [完整功能说明](FULL_FEATURES_README.md)
- [云端部署指南](CLOUD_DEPLOYMENT_GUIDE.md)
- [Windows服务配置](NSSM_INSTALL_GUIDE.md)
- [系统托盘应用](SYSTEM_TRAY_README.md)

## 🔧 配置

复制 `.env.example` 为 `.env` 并修改配置:

```bash
SECRET_KEY=your-random-secret-key
FLASK_DEBUG=False
PORT=7777
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request!

## 📧 联系方式

如有问题,请提交Issue或联系维护者。

---

**注意**: 本项目包含Windows特定的服务配置文件(.bat, .ps1),这些文件仅用于Windows环境。云端部署时会使用跨平台的配置(Docker, Procfile等)。
