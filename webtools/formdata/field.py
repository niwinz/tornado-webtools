from .widgets import Widget
from .exceptions import ValidateError
from . import data_types

class Field(object):
    def __init__(self, datatype, widget=None, required=True, default=None):
        assert isinstance(datatype, data_types.Type), "datatype must be a instance of Type"
        self.datatype = datatype
        self.default = default
        self.required = required
        self.widget = widget

        if self.widget:
            if isinstance(self.widget, type):
                self.widget = self.widget()
            assert isinstance(self.widget, Widget), "widget must be a instance of Widget"

    def clean(self, name, formdata):
        raw_value = formdata.get_argument(name)
        if raw_value:
            return self.datatype.to_python(raw_value, self)
        else:
            if not self.required:
                return self.default
            raise ValidateError("this field is required")


class BoundField(object):
    def __init__(self, name, prefixed_name, field, form):
        self.name = name
        self.prefixed_name = prefixed_name
        self.field = field
        self.form = form

    def __str__(self):
        if not self.field.widget:
            return ""

        value = self.form._initial.get(self.name, None)
        value = self.field.datatype.from_python(value)

        return self.field.widget(self.name, self.prefixed_name, value)

