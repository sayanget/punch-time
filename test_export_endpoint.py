"""
直接测试导出端点以查看实际错误
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟Flask应用上下文
from app import app
from flask import session

# 创建测试客户端
with app.test_client() as client:
    # 首先登录（如果需要）
    # 这里我们直接设置session来模拟已登录状态
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user'
    
    # 测试导出端点
    print("测试 /api/export 端点...")
    try:
        response = client.get('/api/export')
        print(f"\n状态码: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        
        if response.status_code == 200:
            print("\n✅ 导出成功!")
            print(f"响应长度: {len(response.data)} 字节")
            # 显示前500个字符
            preview = response.data.decode('utf-8-sig')[:500]
            print(f"\n预览:\n{preview}")
        else:
            print(f"\n❌ 导出失败!")
            print(f"错误响应: {response.data.decode('utf-8')}")
    except Exception as e:
        print(f"\n❌ 发生异常: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        
        # 打印完整的堆栈跟踪
        import traceback
        print("\n完整错误堆栈:")
        traceback.print_exc()
