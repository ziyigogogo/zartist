class StrParseError(Exception):
    """自定义字符串解析异常类"""

    def __init__(self, s: str, msg: str = ""):
        self.s = s
        self.msg = msg
        super().__init__(f"Failed to parse input string: {s}\nError detail: {msg}")
