from datetime import datetime, timedelta, tzinfo
import pytz

utc = pytz.utc

_localtime = None

def get_default_timezone_name(application=None):
    if application is None:
        from webtools.application import get_app
        application = get_app()
    return application.conf.TZ


def get_default_timezone(application):
    global _localtime

    if _localtime is None:
        default_tzname = get_default_timezone_name(application)
        _localtime = pytz.timezone(default_tzname)

    return _localtime


#def activate(handler, timezone):
#    if isinstance(timezone, tzinfo):
#        _active.value = timezone
#    elif isinstance(timezone, str):
#        _active.value = pytz.timezone(timezone)
#    else:
#        raise ValueError("Invalid timezone: {0}".format(timezone))


def as_localtime(value, timezone):
    value = value.astimezone(timezone)
    value = timezone.normalize(value)
    return value


def get_timezone(name):
    return pytz.timezone(name)


now = lambda: datetime.utcnow().replace(tzinfo=utc)
is_aware = lambda value: value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None
is_naive = lambda value: value.tzinfo is None or value.tzinfo.utcoffset(value) is None

def make_aware(value, timezone):
    return timezone.localize(value, is_dst=None)

def make_naive(value, timezone):
    value = value.astimezone(timezone)
    value = timezone.normalize(value)
    return value.replace(tzinfo=None)

