import unittest

from zartist import str2dict, StrParseError


class TestStr2dict(unittest.TestCase):
    def test_basic_case(self):
        input_text = '{"key": "value"}'
        expected_output = {"key": "value"}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_multiple_dicts(self):
        input_text = '{"a":1} {"b":2}'
        expected_output = {"a": 1}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_nested_dicts(self):
        input_text = '{"outer": {"inner": [1, 2, {"nested": "test"}]}}'
        expected_output = {"outer": {"inner": [1, 2, {"nested": "test"}]}}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_strings_with_quotes(self):
        input_text = "{\"quote\": \"test\"}"
        expected_output = {'quote': 'test'}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_invalid_syntax(self):
        input_text = '{invalid: syntax}'
        with self.assertRaises(StrParseError):
            str2dict(input_text)

    def test_mixed_content(self):
        input_text = 'abc{"valid":1}def[invalid]ghi'
        expected_output = {"valid": 1}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_empty_set(self):
        input_text = '{}'
        expected_output = {}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_escaped_characters(self):
        input_text = r'{r"esca:ped\:": r"\\"}\''
        expected_output = {r'esca:ped\:': r'\\'}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_list_in_dict(self):
        input_text = '{"list_key": [1, 2, 3]}'
        expected_output = {"list_key": [1, 2, 3]}
        self.assertEqual(expected_output, str2dict(input_text))

    def test_ordering_of_matches(self):
        input_text = '{"a":1} {"abcdef":2}'
        expected_output = {"abcdef": 2}
        self.assertEqual(expected_output, str2dict(input_text), )

    def test_complex_input(self):
        input_text = "  {'1':2} 拉萨看得见伐啦发 {'asdf': {'a':[1,2,23,3,1,23,12,31,23,123,123, {'d': 123}], 'df':{'asdfa':{'asdf':{'a':1233123123}}}}}  "
        expected_output = {
            'asdf': {
                'a': [1, 2, 23, 3, 1, 23, 12, 31, 23, 123, 123, {'d': 123}],
                'df': {
                    'asdfa': {
                        'asdf': {'a': 1233123123}
                    }
                }
            }
        }

        self.assertEqual(expected_output, str2dict(input_text))


if __name__ == "__main__":
    unittest.main()
