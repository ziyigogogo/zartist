import unittest

from zartist import str2obj


class TestStr2Obj(unittest.TestCase):
    def test_auto_literal_eval(self):
        test_cases = [
            ("123", 123),
            ("[1, 2, 3]", [1, 2, 3]),
            ("(1, 2, 3)", (1, 2, 3)),
            ("True", True),
            ("False", False),
            ("None", None),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(str2obj(input_str), expected)

    def test_auto_dict(self):
        test_cases = [
            ('{"key": "value"}', {"key": "value"}),
            ('{"numbers": [1, 2, 3]}', {"numbers": [1, 2, 3]}),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(str2obj(input_str), expected)

    def test_force_dict(self):
        input_str = '{"key": "value"}'
        expected = {"key": "value"}
        self.assertEqual(str2obj(input_str, target_type="dict"), expected)

    def test_invalid_target_type(self):
        with self.assertRaises(Exception):
            str2obj("test", target_type="invalid")

    def test_invalid_input(self):
        with self.assertRaises(Exception):
            str2obj("invalid python literal")


if __name__ == "__main__":
    unittest.main()
