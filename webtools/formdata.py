
# Exceptions

class ValidateError(Exception):
    pass


# Utils

def get_declared_fields(bases, attrs, with_base_fields=True):
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]

    if with_base_fields:
        for base in bases[::-1]:
            if hasatr(base, "base_fields"):
                fields = base.base_fields.items() + fields

    return dict(fields)


# Form

class FormDataMeta(type):
    def __new__(cls, name, bases, attrs):
        attrs["base_fields"] = get_declared_fields(bases, attrs)
        return super(FormDataMeta, cls).__new__(cls, name, bases, attrs)


class FormDataBase(object):
    def __init__(self, handler, initial={}, prefix=None):
        self.handler = handler
        self.prefix = None
        self.initial = initial
        self.errors = {}
        self._validated = False

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
                self.errors[field_name] = ["TODO: unexpected field error"]

    def _form_validate(self):
        try:
            self.cleaned_data = self.clean()
        except ValidateError as e:
            self.errors["__global__"] = ["TODO: unexpected global error"]

    def clean(self):
        return self.cleaned_data

    def _form_validate(self):
        pass

    def validate(self):
        self.cleaned_data = {}
        self._field_validate()
        self._form_validate()
        self._validated = True

    def is_valid(self):
        return not bool(errors) and self._validated

    def get_argument(self, name):
        return self.handler.get_arguments(name)


class FormData(FormDataBase, metaclass=FormDataMeta):
    pass


# Fields

class Field(object):
    def __init__(self, typer=None, widget=None, required=True, default=None):
        assert isinstance(typer, Typer), "typer must be a instance of Typer"
        self.typer = typer
        self.default = default

        self.widget = widget
        if self.widget:
            assert isinstance(self.widget, Widget), "widget must be a instance of Widget"
            self.widget.set_field(self)

    def clean(self, name, formdata):
        raw_value = formdata.get_argument(name)
        if not raw_value and not required:
            return self.default

        return self.typer.to_python(raw_value, self)


# Widgets

class Widget(object):
    def set_field(self, field):
        self.field = field


# Typers

class Typer(object):
    def to_python(self, value, field):
        return value


