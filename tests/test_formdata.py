from unittest import TestCase

class HandlerMock(object):
    def __init__(self, arguments):
        self.arguments = arguments

    def get_arguments(self, name):
        if name not in self.arguments:
            return []

        value = self.arguments[name]
        if not isinstance(value, (list, tuple)):
            value = [value]

        return value



from webtools.formdata import FormData, Field, Typer
from webtools.formdata import IntegerTyper, UnicodeTyper
from webtools.formdata import MultipleUnicodeTyper, MultipleIntegerTyper


class TestForm1(FormData):
    field1 = Field(typer=UnicodeTyper())
    field2 = Field(typer=IntegerTyper())

class TestForm2(FormData):
    field1 = Field(typer=UnicodeTyper())
    field2 = Field(typer=IntegerTyper(), required=False)


class FormDataTests(TestCase):
    def test_validate_empty_form(self):
        form = TestForm1()

        with self.assertRaises(RuntimeError):
            form.validate()

    def test_simple_validate_01(self):
        handler = HandlerMock({"field1": "Hola", "field2": "2"})
        form = TestForm1(handler)
        form.validate()

        self.assertTrue(form._validated)
        self.assertFalse(form.errors)
        self.assertTrue(form.is_valid())

    def test_simple_validate_02(self):
        handler = HandlerMock({"field1": "Hola", "field2": "A"})
        form = TestForm1(handler)
        form.validate()

        self.assertTrue(form._validated)
        self.assertFalse(form.is_valid())
        self.assertIn("field2", form.errors)

    def test_simple_validate_03(self):
        handler = HandlerMock({"field1": "Hola"})

        form = TestForm1(handler)
        self.assertNotIn("field1", form._initial)

        form.validate()
        self.assertTrue(form._validated)
        self.assertFalse(form.is_valid())
        self.assertIn("field2", form.errors)
        self.assertIn("field1", form._initial)

