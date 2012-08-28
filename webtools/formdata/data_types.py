from .exceptions import ValidateError

class Type(object):
    def to_python(self, value, field):
        return value

    def from_python(self, value):
        return value


class Integer(Type):
    def to_python(self, value, field):
        if len(value) != 1:
            raise ValidateError("Invalid data")

        try:
            return int(value[0])
        except (ValueError, TypeError) as e:
            raise ValidateError("Invalid data")


class Unicode(Type):
    def to_python(self, value, field):
        if len(value) != 1:
            raise ValidateError("Invalid data")
        return value[0]


class MultipleUnicode(Type):
    pass


class MultipleInteger(Type):
    def to_python(self, value, field):
        try:
            return [int(x) for x in value]
        except (ValueError, TypeError):
            raise ValidateError("Invalid data")
