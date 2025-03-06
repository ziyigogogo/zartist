import os
import unittest

import pandas as pd

from zartist import StrParseError, str2df


class TestStr2Df(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test files
        cls.test_dir = os.path.dirname(__file__)

        # 创建测试数据，包含中文以验证编码
        test_data = pd.DataFrame({
            'A': [1, 2],
            'B': ['测试1', '测试2']  # 使用中文测试编码
        })

        # CSV test file with UTF-8
        cls.csv_utf8_path = os.path.join(cls.test_dir, 'test_utf8.csv')
        test_data.to_csv(cls.csv_utf8_path, index=False, encoding='utf-8')

        # CSV test file with GBK
        cls.csv_gbk_path = os.path.join(cls.test_dir, 'test_gbk.csv')
        test_data.to_csv(cls.csv_gbk_path, index=False, encoding='gbk')

        # JSON test file with UTF-8
        cls.json_path = os.path.join(cls.test_dir, 'test.json')
        test_data.to_json(cls.json_path, force_ascii=False)

        # JSONL test file with UTF-8
        cls.jsonl_path = os.path.join(cls.test_dir, 'test.jsonl')
        test_data.to_json(cls.jsonl_path, orient='records',
                          lines=True, force_ascii=False)

        # Excel test file
        cls.excel_path = os.path.join(cls.test_dir, 'test.xlsx')
        test_data.to_excel(cls.excel_path, index=False)

    def test_csv_utf8_file(self):
        """测试UTF-8编码的CSV文件"""
        df = str2df(self.csv_utf8_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertTrue(all(df.columns == ['A', 'B']))
        self.assertEqual(df.iloc[0]['B'], '测试1')  # 验证中文正确读取

    def test_csv_gbk_file(self):
        """测试GBK编码的CSV文件"""
        df = str2df(self.csv_gbk_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertTrue(all(df.columns == ['A', 'B']))
        self.assertEqual(df.iloc[0]['B'], '测试1')  # 验证中文正确读取

    def test_json_file(self):
        df = str2df(self.json_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertTrue(all(df.columns == ['A', 'B']))
        self.assertEqual(df.iloc[0]['B'], '测试1')  # 验证中文正确读取

    def test_jsonl_file(self):
        df = str2df(self.jsonl_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertTrue(all(df.columns == ['A', 'B']))
        self.assertEqual(df.iloc[0]['B'], '测试1')  # 验证中文正确读取

    def test_excel_file(self):
        df = str2df(self.excel_path)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (2, 2))
        self.assertTrue(all(df.columns == ['A', 'B']))
        self.assertEqual(df.iloc[0]['B'], '测试1')  # 验证中文正确读取

    def test_unsupported_format(self):
        with self.assertRaises(StrParseError):
            str2df('test.txt')

    def test_nonexistent_file(self):
        with self.assertRaises(Exception):
            str2df('nonexistent.csv')

    @classmethod
    def tearDownClass(cls):
        # Clean up test files
        test_files = [cls.csv_utf8_path, cls.csv_gbk_path,
                      cls.json_path, cls.jsonl_path, cls.excel_path]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)


if __name__ == "__main__":
    unittest.main()
