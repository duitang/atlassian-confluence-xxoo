# encoding=utf-8

from datetime import datetime

from pytz import timezone, utc


APP_TIME_ZONE = timezone('Asia/Shanghai')


def get_local_now():
    return datetime.now(APP_TIME_ZONE)


def local2utc(dt):
    """local naive time to utc"""
    try:
        dt = APP_TIME_ZONE.localize(dt)
    except:
        pass
    return dt.astimezone(utc)


def utc2local(dt):
    """utc time to local"""
    try:
        dt = utc.localize(dt)
    except:
        pass
    return dt.astimezone(APP_TIME_ZONE)


def aware2naive(dt):
    return dt.replace(tzinfo=None)


def naive2aware(dt, tz=APP_TIME_ZONE):
    return tz.localize(dt)


def format_time(dt, format='%Y-%m-%d %H:%M:%S'):
    return dt.strftime(format)
