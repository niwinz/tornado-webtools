from datetime import datetime, timedelta, tzinfo
from threading import local
import pytz

utc = pytz.utc

_active = local()
_localtime = None

def set_default_timezone_name(tzname):
    _active.default_timezone_name = tzname

def get_default_timezone_name():
    return _active.default_timezone_name

def get_default_timezone():
    global _localtime

    if _localtime is None:
        default_tzname = get_default_timezone_name()
        _localtime = pytz.timezone(default_tzname)

    return _localtime

def get_timezone_name(timezone):
    return timezone.zone

def get_current_timezone():
    return getattr(_active, "value", get_default_timezone())

def get_current_timezone_name():
    return get_timezone_name(get_current_timezone())

def activate(timezone):
    if isinstance(timezone, tzinfo):
        _active.value = timezone
    elif isinstance(timezone, str):
        _active.value = pytz.timezone(timezone)
    else:
        raise ValueError("Invalid timezone: {0}".format(timezone))

def deactivate():
    if hasattr(_active, "value"):
        del _active.value

def as_localtime(value, timezone=None):
    if timezone is None:
        timezone = get_current_timezone()

    value = value.astimezone(timezone)
    value = timezone.normalize(value)
    return value


now = lambda: datetime.utcnow().replace(tzinfo=utc)
is_aware = lambda value: value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None
is_naive = lambda value: value.tzinfo is None or value.tzinfo.utcoffset(value) is None

def make_aware(value, timezone):
    return timezone.localize(value, is_dst=None)

def make_naive(value, timezone):
    value = value.astimezone(timezone)
    value = timezone.normalize(value)
    return value.replace(tzinfo=None)

