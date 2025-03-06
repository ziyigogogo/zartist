"""
全局测试配置和共享fixture
"""
import pytest
from typing import Dict, Any


@pytest.fixture(scope="session")
def dict_test_cases() -> Dict[str, Dict[str, Any]]:
    """
    提供一组通用的字典测试用例，可以被多个测试模块复用
    返回一个字典，其中包含测试用例名称和预期的输入输出
    """
    return {
        "empty": {
            "input": "{}",
            "expected": {}
        },
        "invalid_syntax": {
            "input": "{invalid: syntax}",
            "raises": "StrParseError"
        },
        "nested_complex": {
            "input": '{"a": {"b": [1, {"c": "d"}]}}',
            "expected": {"a": {"b": [1, {"c": "d"}]}}
        }
    }


@pytest.fixture(scope="function")
def cleanup_test_files(request):
    """
    用于需要创建临时文件的测试
    测试结束后自动清理
    """
    import os
    temp_files = []

    def _add_temp_file(filepath):
        temp_files.append(filepath)
        return filepath

    def _cleanup():
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception:
                pass

    request.addfinalizer(_cleanup)
    return _add_temp_file
