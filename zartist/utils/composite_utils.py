from ast import literal_eval

from zartist.utils.builtin_utils import str2dict
from zartist.errors import StrParseError
from zartist.utils.image_utils import str2pil
from zartist.utils.pandas_utils import str2df


def str2obj(s: str, target_type="auto"):
    """从字符串中提取支持的对象"""
    supported_types = ["dict", "pil", "df"]
    try:
        match target_type:
            case "auto":
                try:
                    return literal_eval(s)
                except (ValueError, SyntaxError, MemoryError, RecursionError):
                    for t in supported_types:
                        try:
                            return str2obj(s, t)
                        except Exception:
                            continue
                    raise TypeError(f"Failed to parse any supported type")
            case "dict":
                return str2dict(s)
            case "pil":
                return str2pil(s)
            case "df":
                return str2df(s)
            case _:
                raise TypeError(f"Unsupported type: {target_type}")
    except Exception as e:
        raise StrParseError(s, f"@str2obj: an error occurred: {e}")


if __name__ == "__main__":
    a = str2obj("{'A':\"B\"}")
    print(a)
