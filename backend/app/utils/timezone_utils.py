from datetime import datetime, date, time, timezone
import pytz

def get_profile_timezone(tz_name: str):
    try:
        return pytz.timezone(tz_name or "UTC")
    except Exception:
        return pytz.UTC

def get_current_time_in_tz(tz_name: str) -> datetime:
    tz = get_profile_timezone(tz_name)
    return datetime.now(tz)

def get_today_in_tz(tz_name: str) -> date:
    return get_current_time_in_tz(tz_name).date()

def format_time_hh_mm(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def parse_time_hh_mm(time_str: str) -> time:
    parts = time_str.strip().split(":")
    return time(int(parts[0]), int(parts[1]))

def is_time_passed_by_minutes(scheduled_time_str: str, target_date: date, tz_name: str, minutes_threshold: int = 30) -> bool:
    """Checks if the scheduled time on target_date has passed by at least minutes_threshold in tz_name."""
    now_tz = get_current_time_in_tz(tz_name)
    tz = get_profile_timezone(tz_name)
    
    t = parse_time_hh_mm(scheduled_time_str)
    naive_dt = datetime.combine(target_date, t)
    sched_dt = tz.localize(naive_dt)
    
    delta = (now_tz - sched_dt).total_seconds() / 60.0
    return delta >= minutes_threshold
