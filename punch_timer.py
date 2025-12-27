import argparse
import json
import sys
from datetime import datetime, date, time, timedelta
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


DATA_FILE = Path(__file__).with_name("punches.json")


def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_time(value, target_date):
    try:
        if len(value) <= 5 and ":" in value:
            h, m = map(int, value.split(":"))
            return datetime.combine(target_date, time(hour=h, minute=m))
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"无效时间格式: {value}") from exc


def record_punch(punch_date, punch_time):
    data = load_data()
    day_key = punch_date.isoformat()
    times = [datetime.fromisoformat(ts) for ts in data.get(day_key, [])]
    if len(times) >= 4:
        raise SystemExit("当日已满4次打卡，无法继续记录。")
    times.append(punch_time)
    times.sort()
    data[day_key] = [ts.isoformat() for ts in times]
    save_data(data)
    print(f"已记录 {day_key} 第 {len(times)} 次打卡: {punch_time.time()}" )


def compute_duration(punch_date):
    data = load_data()
    day_key = punch_date.isoformat()
    raw_times = data.get(day_key, [])
    if not raw_times:
        raise SystemExit("该日期暂无打卡记录。")
    times = sorted(datetime.fromisoformat(ts) for ts in raw_times)
    if len(times) < 4:
        missing = 4 - len(times)
        raise SystemExit(f"记录不足4次，缺少 {missing} 次。")
    t1, t2, t3, t4 = times[:4]
    if t2 <= t1 or t4 <= t3:
        raise SystemExit("时间顺序异常，请检查打卡顺序。")
    total = (t2 - t1) + (t4 - t3)
    print(f"日期: {day_key}")
    print(f"第1次: {t1.time()}  第2次: {t2.time()}  间隔: {fmt_delta(t2 - t1)}")
    print(f"第3次: {t3.time()}  第4次: {t4.time()}  间隔: {fmt_delta(t4 - t3)}")
    print(f"每日打卡时长: {fmt_delta(total)}")


def fmt_delta(delta):
    seconds = int(delta.total_seconds())
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    parser = argparse.ArgumentParser(description="每日4次打卡，计算工作时长")
    sub = parser.add_subparsers(dest="command", required=True)

    punch_parser = sub.add_parser("punch", help="记录打卡时间，默认当前时间")
    punch_parser.add_argument("--time", dest="time_str", help="时间，格式HH:MM或完整ISO时间")
    punch_parser.add_argument("--date", dest="date_str", help="日期，格式YYYY-MM-DD，默认今日")

    report_parser = sub.add_parser("report", help="查看某日打卡时长")
    report_parser.add_argument("--date", dest="date_str", help="日期，格式YYYY-MM-DD，默认今日")

    args = parser.parse_args()
    target_date = date.fromisoformat(args.date_str) if args.date_str else date.today()

    if args.command == "punch":
        punch_time = parse_time(args.time_str, target_date) if args.time_str else datetime.now()
        record_punch(target_date, punch_time)
    elif args.command == "report":
        compute_duration(target_date)


if __name__ == "__main__":
    main()
