import os


class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 服务配置
    SERVICE_NAME = "PunchTimerService"
    SERVICE_DISPLAY_NAME = "打卡计时器服务"
    SERVICE_DESCRIPTION = "打卡计时器Web服务"
    
    # 网络配置
    HOST = '0.0.0.0'
    PORT = 7777
    
    # 日志配置
    LOG_FILE = 'punch_timer_service.log'
    LOG_LEVEL = 'INFO'
    
    # 托盘图标配置
    TRAY_ICON_UPDATE_INTERVAL = 5  # 秒