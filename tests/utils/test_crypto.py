import unittest


class CryptoModuleTests(unittest.TestCase):
    def test_get_random_string(self):
        from webtools.utils.crypto import get_random_string
        res = get_random_string()

        self.assertEqual(len(res), 12)
        self.assertIsInstance(res, str)

    def test_constant_time_compare(self):
        from webtools.utils.crypto import constant_time_compare
        self.assertTrue(constant_time_compare("hello", "hello"))

    def test_pbkdf2(self):
        from webtools.utils.crypto import pbkdf2
        res = pbkdf2("test", "some-salt", 10)
        self.assertEqual(res, b'X\xf0\xdd\xea3\x0b\x9b.\xe8\xad\x1a\xb8}\x90\xb5i\xd3a"\x9as\x1f\xa3\x8d\x17\xff\xff\x8f\r\xb2\xaf\x7f')
