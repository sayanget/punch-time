"""
触发导出并监控服务器错误
这个脚本会模拟浏览器请求来触发实际的错误
"""
import requests
import time

print("准备触发导出端点...")
print("请确保您已在浏览器中登录")
print()

# 尝试获取session cookie
print("提示：请在浏览器的开发者工具中：")
print("1. 打开 Application/Storage > Cookies")
print("2. 找到 'session' cookie的值")
print("3. 复制该值")
print()

session_cookie = input("请粘贴session cookie值（或直接按Enter跳过）: ").strip()

if session_cookie:
    # 使用提供的session cookie
    cookies = {'session': session_cookie}
    
    print("\n发送导出请求...")
    try:
        response = requests.get('http://localhost:7777/api/export', cookies=cookies)
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.content_type}")
        
        if response.status_code == 200:
            if 'text/csv' in response.content_type:
                print("\n✅ 导出成功!")
                content = response.text
                print(f"\nCSV内容:\n{content[:500]}")
            else:
                print(f"\n响应内容:\n{response.text[:500]}")
        else:
            print(f"\n❌ 错误响应:")
            print(response.text[:1000])
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
else:
    print("\n跳过cookie测试")
    print("\n请在浏览器中点击导出按钮，然后查看服务器终端的错误输出")
    print("服务器应该会显示详细的错误堆栈信息")
