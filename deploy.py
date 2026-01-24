#!/usr/bin/env python3
"""
打卡计时器 - 本地一键部署脚本 (跨平台)
支持 Windows, macOS, Linux
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)

def print_step(step, total, text):
    """打印步骤"""
    print(f"\n[{step}/{total}] {text}...")

def print_success(text):
    """打印成功消息"""
    print(f"✓ {text}")

def print_error(text):
    """打印错误消息"""
    print(f"✗ {text}")

def print_info(text):
    """打印信息"""
    print(f"ℹ {text}")

def check_python_version():
    """检查Python版本"""
    print_step(1, 5, "检查Python环境")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python版本过低: {version_str}")
        print_info("需要Python 3.8或更高版本")
        print_info("请访问 https://www.python.org/downloads/ 下载")
        return False
    
    print_success(f"Python版本: {version_str}")
    return True

def check_dependencies():
    """检查并安装依赖"""
    print_step(2, 5, "检查依赖包")
    
    try:
        import flask
        print_success("依赖包已安装")
        return True
    except ImportError:
        print_error("缺少依赖包")
        print_info("正在安装依赖...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print_success("依赖安装成功")
            return True
        except subprocess.CalledProcessError:
            print_error("依赖安装失败")
            print_info("请手动运行: pip install -r requirements.txt")
            return False

def generate_ssl_certificate():
    """生成SSL证书"""
    print_step(3, 5, "检查SSL证书")
    
    ssl_dir = Path("ssl")
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    if cert_file.exists() and key_file.exists():
        print_success("SSL证书已存在")
        return True
    
    print_info("正在生成SSL证书...")
    
    try:
        subprocess.check_call([sys.executable, "generate_ssl_cert.py"])
        print_success("SSL证书生成成功")
        return True
    except subprocess.CalledProcessError:
        print_error("SSL证书生成失败")
        return False

def initialize_database():
    """初始化数据库"""
    print_step(4, 5, "初始化数据库")
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    print_success("数据库目录已准备")
    return True

def start_server():
    """启动服务器"""
    print_step(5, 5, "启动HTTPS服务器")
    
    print("\n" + "=" * 50)
    print("  服务器启动中...")
    print("=" * 50)
    print("\n访问地址: https://localhost:7778")
    print("\n提示:")
    print("  • 浏览器会显示安全警告(自签名证书)")
    print("  • 点击\"高级\"然后\"继续访问localhost\"即可")
    print("  • 按 Ctrl+C 停止服务器")
    print("\n" + "=" * 50 + "\n")
    
    # 设置环境变量
    os.environ["SSL_ENABLED"] = "true"
    os.environ["SSL_CERT_PATH"] = "ssl/cert.pem"
    os.environ["SSL_KEY_PATH"] = "ssl/key.pem"
    os.environ["HTTPS_PORT"] = "7778"
    
    # 延迟打开浏览器
    def open_browser():
        time.sleep(3)
        webbrowser.open("https://localhost:7778")
    
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # 启动Flask应用
    try:
        subprocess.call([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("  服务器已停止")
        print("=" * 50)

def main():
    """主函数"""
    print_header("打卡计时器 - 本地一键部署")
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 生成SSL证书
    if not generate_ssl_certificate():
        return 1
    
    # 初始化数据库
    if not initialize_database():
        return 1
    
    # 启动服务器
    start_server()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n部署已取消")
        sys.exit(0)
    except Exception as e:
        print_error(f"发生错误: {e}")
        sys.exit(1)
