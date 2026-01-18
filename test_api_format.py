"""
测试脚本：验证API返回的数据格式
"""
import requests
import json

# 测试本地环境
LOCAL_URL = "http://localhost:7777"

def test_api():
    print("测试API数据格式...")
    print("="*60)
    
    # 注意：需要先登录才能访问API
    print("\n⚠️  此脚本需要在已登录的浏览器中运行")
    print("或者修改脚本添加登录逻辑\n")
    
    try:
        # 测试API端点
        response = requests.get(f"{LOCAL_URL}/api/punches")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ API响应成功")
            print(f"\n返回的数据结构：")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 分析数据结构
            if data:
                first_date = list(data.keys())[0]
                first_records = data[first_date]
                print(f"\n第一个日期: {first_date}")
                print(f"记录数: {len(first_records)}")
                
                if first_records:
                    first_record = first_records[0]
                    print(f"\n第一条记录的类型: {type(first_record)}")
                    print(f"第一条记录的内容: {first_record}")
                    
                    if isinstance(first_record, dict):
                        print("\n✓ 记录是对象格式（新格式）")
                        print(f"  包含的字段: {list(first_record.keys())}")
                    elif isinstance(first_record, str):
                        print("\n✓ 记录是字符串格式（旧格式）")
        else:
            print(f"✗ API响应失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")

if __name__ == "__main__":
    test_api()
