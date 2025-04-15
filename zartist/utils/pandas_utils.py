import pandas as pd
from zartist.errors import StrParseError


def str2df(s: str):
    """从字符串中提取DataFrame对象"""
    file_ext = s.split('.')[-1].lower()
    try:
        for encoding in ['utf-8', 'gbk']:
            try:
                match file_ext:
                    case 'json':
                        return pd.read_json(s, encoding=encoding)
                    case 'jsonl':
                        return pd.read_json(s, lines=True, encoding=encoding)
                    case 'xlsx' | 'xls':
                        return pd.read_excel(s)
                    case 'csv':
                        return pd.read_csv(s, encoding=encoding)
                    case _:
                        raise TypeError(f"Unsupported file extension: {file_ext}")
            except UnicodeDecodeError:
                continue
        raise TypeError("Failed to parse DataFrame in any encoding")
    except Exception as e:
        raise StrParseError(s, f"@str2df: an error occurred: {e}")
