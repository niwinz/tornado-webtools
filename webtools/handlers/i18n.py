from tornado import locale
from webtools.utils.timezone import get_default_timezone, get_timezone


class I18nMixin(object):
    def get_browser_locale(self, default=None):
        """
        Overwrite default behavior with correct
        setting the default language.
        """
        if default is None:
            default = self.conf.I18N_DEFAULT_LANG
        return super(I18nMixin, self).get_browser_locale(default=default)

    def get_user_locale(self):
        if "webtools_locale" in self.session:
            return locale.get(self.session["webtools_locale"])
        return None

    def _(self, message, plural_message=None, count=None):
        self.locale.translate(message, plural_message=plural_message, count=count)

    def activate_locale(self, locale_name):
        """
        Activate a specific locale for current user.
        """
        self.session["webtools_locale"] = locale_name
        self._locale = locale.get(locale_name)


class TimezoneMixin(object):
    @property
    def timezone(self):
        if not hasattr(self, "_timezone"):
            self._timezone = self.get_user_timezone()
        return self._timezone

    def get_user_timezone(self):
        if "webtools_timezone" in self.session:
            return get_timezone(self.session["webtools_timezone"])
        return get_timezone(self.application.conf.DEFAULT_TZ)

    def activate_timezone(self, timezone_name):
        self.session["webtools_timezone"] = timezone_name
        self._timezone = get_timezone(timezone_name)
