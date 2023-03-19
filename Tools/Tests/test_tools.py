from unittest import TestCase

from Maxs_Modules.tools import sort_multi_array, string_bool, ip_address, set_if_none, try_convert


class TestTools(TestCase):

    def test_sort_multi_array(self):
        result = sort_multi_array([['Max', 'Bot 1', 'Bot 2', 'Bot 3'], [-3, 1, 1, -1]])
        self.assertEqual(result, [['Max', 'Bot 3', 'Bot 1', 'Bot 2'], [-3, -1, 1, 1]])

    def test_sort_multi_array_down(self):
        result = sort_multi_array([['Max', 'Bot 1', 'Bot 2', 'Bot 3'], [-3, 1, 1, -1]], True)
        self.assertEqual(result, [['Bot 1', 'Bot 2', 'Bot 3', 'Max'], [1, 1, -1, -3]])

    def test_string_bool_true(self):
        result = string_bool("True")
        self.assertEqual(result, True)

    def test_string_bool_false(self):
        result = string_bool("False")
        self.assertEqual(result, False)

    def test_ip_address(self):
        result = ip_address("192.168.3.1")
        self.assertEqual(result, "192.168.3.1")

    def test_set_if_none_not(self):
        name = "Max"
        result = set_if_none(name, "Bob")
        self.assertEqual(result, "Max")

    def test_set_if_none_is(self):
        name = None
        result = set_if_none(name, "Bob")
        self.assertEqual(result, "Bob")

    def test_try_convert_int(self):
        result = try_convert("1", int, True)
        self.assertEqual(result, 1)

    def test_try_convert_str(self):
        result = try_convert("string", str, True)
        self.assertEqual(result, "string")

    def test_try_convert_fail(self):
        result = try_convert("string", int, True)
        self.assertEqual(result, None)
