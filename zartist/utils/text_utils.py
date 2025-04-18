from ast import literal_eval
import json
import regex
from zartist import logger

from zartist.errors import StrParseError


def str2dict(s: str):
    """从字符串中提取字典对象"""

    def greedy_s2d(s: str) -> dict:
        # 贪心查找字符串中可能是字典的部分
        pattern = r"""
            (?P<valid_dict>                               # 命名捕获组，用于匹配有效的字典
                \{                                        # 匹配字典的开始符号 '{'
                (?:                                       # 非捕获组，用于匹配字典内容
                    [^{}"'()]                             # 匹配非特殊字符
                    | "(?:\\.|[^"])*"                     # 匹配双引号字符串
                    | '(?:\\.|[^'])*'                     # 匹配单引号字符串
                    | (?&valid_dict)                      # 递归匹配嵌套的字典
                    | $$(?:[^[$$]|(?&valid_dict))*\]      # 匹配嵌套的列表
                    | $(?:[^()]|(?&valid_dict))*$         # 匹配嵌套的括号
                )*                                        # 重复匹配内容
                \}                                        # 匹配字典的结束符号 '}'
            )
        """
        try:
            matches = regex.findall(pattern, s, regex.VERBOSE | regex.DOTALL)
            matches.sort(key=len, reverse=True)
            for m in matches:
                try:
                    d = literal_eval(m)
                    if isinstance(d, dict):
                        return d
                except Exception:
                    continue
            raise TypeError(f"Failed to parse any matches from string: {s}")
        except Exception as e:
            raise StrParseError(s, f"@str2dict: an error occurred: {e}")

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return greedy_s2d(s)


def clean_text(s: str) -> str:
    # Strip leading/trailing whitespace and replace all internal whitespace with single space
    return ' '.join(s.strip().split())


if __name__ == "__main__":
    logger.info(str2dict("123123 {\"a\": {\"b\": [1,2,3,{\"c\": 4}]}}"))
