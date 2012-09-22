
from webtools.utils.encoding import smart_text
from .base import Service

def locale_to_code(locale):
    """
    Get main code from locale object.
    """
    code = locale.code
    return code.split("_")[0]


class LocaleService(object):
    def get_format(self, format_name, lang=None, handler=None):
        """
        Get format by name from global settings.
        """
        if lang is None and handler is None:
            raise RuntimeError("One of parameters 'lang' or 'handler' is mandatory")

        format_name = smart_text(format_name)

        if lang is None:
            lang = locale_to_code(handler.locale)

        # At the moment only get formats from settings
        # In near future i go to implement full locale depenen
        # format module.

        return getattr(handler.conf, format_name)
