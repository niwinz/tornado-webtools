# -*- coding: utf-8 -*-

from importlib import import_module

def load_class(path):
    """
    Load class from path.
    """

    mod_name, klass_name = None, None

    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except AttributeError as e:
        raise RuntimeError("Error importing {0}: '{1}'".format(mod_name, e))

    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise RuntimeError('Module "{0}" does not define a "{1}" class'.format(mod_name, klass_name))

    return klass
