from __future__ import annotations

import datetime as dt

import pytz

AR_WEEKDAYS = [
    "الاثنين",
    "الثلاثاء",
    "الأربعاء",
    "الخميس",
    "الجمعة",
    "السبت",
    "الأحد",
]


def cairo_tz(timezone_name: str) -> dt.tzinfo:
    return pytz.timezone(timezone_name)


def now_in_tz(tz: dt.tzinfo) -> dt.datetime:
    return dt.datetime.now(tz)


def start_of_today(tz: dt.tzinfo) -> dt.datetime:
    now = now_in_tz(tz)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def arabic_weekday_name(d: dt.date) -> str:
    # Python: Monday=0..Sunday=6
    return AR_WEEKDAYS[d.weekday()]


def format_arabic_time(t: dt.time) -> str:
    hour = t.hour
    minute = t.minute
    suffix = "ص" if hour < 12 else "م"
    hour12 = hour % 12
    if hour12 == 0:
        hour12 = 12
    return f"{hour12:02d}:{minute:02d} {suffix}"

