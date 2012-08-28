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
            assert isinstance(self.widget, Widget), "widget must be a instance of Widget"
            self.widget.set_field(self)

    def clean(self, name, formdata):
        raw_value = formdata.get_argument(name)
        if raw_value:
            return self.datatype.to_python(raw_value, self)
        else:
            if not self.required:
                return self.default
            raise ValidateError("this field is required")
