import copy

class Widget(object):
    """
    Base class for all formdata widgets.
    """

    def __init__(self, attrs={}):
        self.attrs = attrs

    def set_field(self, field):
        self.field = field

    def render(self, name, prefixed_name, value):
        raise NotImplementedError()

    def attrs_to_str(self, attrs):
        return " ".join(['{key}="{val}"'.format(key=x, val=y)
            for x,y in attrs.items()])

    def __call__(self, name, prefixed_name, value):
        return self.render(name, prefixed_name, value)


class InputText(Widget):
    def render(self, name, prefixed_name, value):
        attrs = {"type": "text", "name": prefixed_name}
        if value:
            attrs["value"] = value

        attrs.update(self.attrs)
        return "<input {0}></input>".format(self.attrs_to_str(attrs))


class Textarea(Widget):
    def render(self, name, prefixed_name, value):
        attrs = {"name": prefixed_name}
        return "<textarea {0}>{1}</textarea>".format(
                    self.attrs_to_str(attrs), value or "")
