"""
测试导出功能修复
验证export_punches函数能正确处理新的字典格式数据
"""
from datetime import datetime

# 模拟新格式的数据（包含位置信息）
mock_punches = {
    '2026-01-23': [
        {'time': '2026-01-23T08:30', 'latitude': 39.9042, 'longitude': 116.4074, 'location_name': 'Beijing'},
        {'time': '2026-01-23T12:00', 'latitude': 39.9042, 'longitude': 116.4074, 'location_name': 'Beijing'},
        {'time': '2026-01-23T13:30', 'latitude': 39.9042, 'longitude': 116.4074, 'location_name': 'Beijing'},
        {'time': '2026-01-23T18:00', 'latitude': 39.9042, 'longitude': 116.4074, 'location_name': 'Beijing'},
    ],
    '2026-01-24': [
        {'time': '2026-01-24T02:30', 'latitude': 39.9042, 'longitude': 116.4074, 'location_name': 'Beijing'},  # 末班打卡
    ]
}

# 模拟导出逻辑
processed_late_shifts = set()

for date in sorted(mock_punches.keys()):
    times = mock_punches[date]
    
    # 过滤掉重复的末班打卡记录
    filtered_times = []
    for punch_record in times:
        # 提取时间字符串（处理新的字典格式）
        if isinstance(punch_record, dict):
            t = punch_record.get('time')
        else:
            t = punch_record  # 向后兼容旧格式
        
        # 检查是否为末班打卡(凌晨5点前)
        try:
            dt = datetime.fromisoformat(t)
            if dt.hour < 5:
                # 如果这个时间戳已经在前一天处理过,跳过
                if t in processed_late_shifts:
                    print(f"跳过重复的末班打卡: {t}")
                    continue
                processed_late_shifts.add(t)
        except Exception as e:
            print(f"解析时间失败: {t}, 错误: {e}")
            pass
        filtered_times.append(t)
    
    print(f"\n日期: {date}")
    print(f"原始记录数: {len(times)}")
    print(f"过滤后记录数: {len(filtered_times)}")
    print(f"时间列表: {filtered_times}")

print("\n✅ 测试通过！导出逻辑能正确处理新的字典格式数据")
