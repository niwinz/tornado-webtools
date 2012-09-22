import jinja2

from webtools.utils.timezone import as_localtime, is_naive, is_aware, make_aware, get_timezone, get_default_timezone

@jinja2.contextfunction
def ugettext(context, message, plural_message=None, count=None):
    """
    Translate template text tu current locale.
    """
    handler = context["handler"]
    return handler.locale.translate(message, plural_message=plural_message, count=count)


@jinja2.contextfilter
def date(context, value, format=None, tz=None):
    handler = context["handler"]
    if tz is not None:
        timezone = get_timezone(tz)
    else:
        timezone = handler.timezone

    if is_naive(value):
        value = make_aware(value, get_default_timezone(handler.application))

    # TODO: full django like formate subsystem
    return as_localtime(value, timezone)
