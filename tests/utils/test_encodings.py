import unittest


class EncodignModuleTests(unittest.TestCase):
    def test_smart_bytes_1(self):
        from webtools.utils.encoding import smart_bytes

        res1 = smart_bytes("Hello")
        self.assertIsInstance(res1, bytes)

    def test_smart_bytes_2(self):
        from webtools.utils.encoding import smart_bytes

        res1 = smart_bytes("Hello", "ascii")
        self.assertIsInstance(res1, bytes)

    def test_smart_bytes_3(self):
        from webtools.utils.encoding import smart_bytes

        res1 = smart_bytes(2)
        self.assertIsInstance(res1, bytes)
        self.assertEqual(res1, b"2")

    def test_smart_text_1(self):
        from webtools.utils.encoding import smart_text

        res = smart_text(b"Foo")
        self.assertIsInstance(res, str)

    def test_smart_text_2(self):
        from webtools.utils.encoding import smart_text

        res = smart_text(2)
        self.assertIsInstance(res, str)
        self.assertEqual(res, "2")
