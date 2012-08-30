from .exceptions import ValidateError
from .field import Field, BoundField

import copy


def get_declared_fields(bases, attrs, with_base_fields=True):
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in list(attrs.items()) if isinstance(obj, Field)]

    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, "base_fields"):
                fields = list(base.base_fields.items()) + fields

    return dict(fields)


class FormDataMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["base_fields"] = get_declared_fields(bases, attrs)
        return super(FormDataMeta, cls).__new__(cls, name, bases, attrs)



class FormDataBase(object):
    def __init__(self, handler=None, initial={}, prefix=None):
        self.handler = handler
        self.initial = initial

        self.prefix = None
        self.errors = {}

        self._validated = False
        self._initial = copy.deepcopy(self.initial)

    def with_prefix(self, name):
        if self.prefix is None:
            return name
        return "{0}-{1}".format(self.prefix, name)

    def _field_validate(self):
        for field_name, field in self.base_fields.items():
            field_name_with_prefix = self.with_prefix(field_name)
            try:
                value = field.clean(field_name_with_prefix, self)
                if not field.required and value is None:
                    continue

                self.cleaned_data[field_name] = value

            except ValidateError as e:
                self.errors[field_name] = list(e.args)

    def _form_validate(self):
        try:
            self.cleaned_data = self.clean()
        except ValidateError as e:
            self.errors["__global__"] = list(e.args)

    def clean(self):
        return self.cleaned_data

    def validate(self):
        if self.handler is None:
            raise RuntimeError("Cannot validate form without handler instance")

        self.cleaned_data = {}
        self._field_validate()
        self._form_validate()
        self._validated = True

        self._initial.update(self.cleaned_data)

    def is_valid(self):
        return not bool(self.errors) and self._validated

    def get_argument(self, name):
        return self.handler.get_arguments(name)

    def __getitem__(self, name):
        if name in self.base_fields:
            return BoundField(name, self.with_prefix(name), self.base_fields[name], self)

        raise KeyError("{0} field does not exists".format(name))

    def __getattr__(self, name):
        return self[name]


class FormData(FormDataBase, metaclass=FormDataMeta):
    pass
