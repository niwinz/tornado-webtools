# -*- coding: utf-8 -*-

import types
import functools


class ServiceDescriptor(object):
    def __init__(self, service, instance, owner):
        self.service = service
        self.instance = instance
        self.owner = owner

    def __getattr__(self, name):
        _method = getattr(self.service, name)
        if isinstance(_method, types.MethodType):
            return functools.partial(_method, handler=self.instance)
        return _method


class Service(objects):
    """
    Base class for all services.
    """
    def __get__(self, instance, owner):
        return ServiceDescriptor(self, instance, owner)

