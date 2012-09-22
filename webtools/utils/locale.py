# -*- coding: utf-8 -*-

from tornado import locale as t_locale

import os
import os.path
import gettext


class WebtoolsTranslation(gettext.GNUTranslations):
    def __init__(self, *args, **kwargs):
        super(WebtoolsTranslation, self).__init__(*args, **kwargs)
        self.set_output_charset('utf-8')

    def merge(self, other):
        self._catalog.update(other._catalog)


def _load_translation(directory, domain):
    for lang in os.listdir(directory):
        if lang.startswith('.'):
            continue
        if os.path.isfile(os.path.join(directory, lang)):
            continue

        if not os.path.exists(os.path.join(directory, lang, "LC_MESSAGES", domain + ".mo")):
            continue

        gettext_translations = gettext.translation(domain, directory, languages=[lang], class_=WebtoolsTranslation)
        if lang in t_locale._translations:
            t_locale._translations[lang].merge(gettext_translations)
        else:
            t_locale._translations[lang] = gettext_translations



def load_gettext_translations(directories, domain):
    assert isinstance(directories, (tuple, list, set, frozenset)), "directories must be a list or tuple"

    t_locale._translations = {}
    t_locale._use_gettext = True
    for directory in set(directories):
        if not os.path.exists(directory):
            continue

        _load_translation(directory, domain)

    t_locale._supported_locales = frozenset(t_locale._translations.keys())


def set_default_locale(*args, **kwargs):
    return t_locale.set_default_locale(*args, **kwargs)
