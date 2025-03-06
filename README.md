# ZArtist Project

## 运行测试

1. 安装测试依赖：

```bash
pip install -r requirements.txt
```

2. 运行所有测试：

```bash
pytest
```

3. 查看测试覆盖率报告：
运行测试后，会在 `htmlcov` 目录生成覆盖率报告，用浏览器打开 `htmlcov/index.html` 查看。

## 项目目录结构

```
zartist/
├── README.md           # 项目说明文档
├── requirements.txt    # 项目依赖
├── setup.py           # 安装配置
├── pytest.ini         # pytest配置文件
├── zartist/           # 主代码目录
│   ├── __init__.py
│   └── str_utils.py   # 字符串工具模块
└── tests/             # 测试目录
    ├── conftest.py    # 测试配置和共享fixture
    ├── __init__.py
    └── test_str_utils/     # str_utils模块的测试
        ├── __init__.py
        └── test_str2dict.py # str2dict函数的测试用例
