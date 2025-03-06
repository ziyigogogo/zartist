# ZArtist Project

ZArtist 是一个强大的 Python 工具库，专注于图像处理、数据转换和 AI 模型集成。

## 主要功能

- **图像处理工具**
  - 图像格式转换（PIL/Base64/URL）
  - 边界框绘制和可视化
  - 图像标注工具

- **数据转换工具**
  - 字符串转字典
  - 字符串转 DataFrame
  - 复合对象转换

- **AI 模型集成**
  - 通用 LLM 客户端接口
  - Qwen-VL 模型集成
  - 图像分析能力

## 安装

```bash
pip install -r requirements.txt
```

## 项目结构

```
zartist/
├── README.md           # 项目说明文档
├── requirements.txt    # 项目依赖
├── setup.py           # 安装配置
├── pytest.ini         # pytest配置文件
├── zartist/           # 主代码目录
│   ├── __init__.py
│   ├── abc/          # 抽象基类
│   │   ├── __init__.py
│   │   └── base_client.py
│   ├── clients/      # 模型客户端实现
│   │   ├── __init__.py
│   │   └── qwen_vl.py
│   └── utils/        # 工具模块
│       ├── __init__.py
│       ├── builtin_utils.py    # 内置类型工具
│       ├── composite_utils.py  # 复合对象工具
│       ├── image_utils.py      # 图像处理工具
│       ├── pandas_utils.py     # 数据处理工具
│       └── visualization_utils.py  # 可视化工具
└── tests/            # 测试目录
    ├── __init__.py
    ├── conftest.py   # 测试配置
    └── test_utils/   # 工具模块测试
        ├── __init__.py
        ├── test_builtin_utils.py
        ├── test_composite_utils.py
        ├── test_image_utils.py
        ├── test_pandas_utils.py
        └── test_visualization_utils.py
```

## 使用示例

### 图像处理

```python
from zartist.utils.image_utils import str2pil, process_image_reprs
from zartist.utils.visualization_utils import draw_bounding_boxes

# 加载图像
image = str2pil("path/to/image.jpg")  # 支持本地路径、URL 或 Base64

# 处理多个图像
images = process_image_reprs([
    "path/to/image1.jpg",
    "http://example.com/image2.jpg",
    "base64_encoded_image"
])

# 绘制边界框
boxes = '[{"label": "dog", "bbox_2d": [50, 50, 150, 150]}]'
result = draw_bounding_boxes(image, boxes, input_width=200, input_height=200)
```

### 数据转换

```python
from zartist.utils.composite_utils import str2obj
from zartist.utils.pandas_utils import str2df

# 自动类型检测和转换
data = str2obj('{"key": "value"}')  # 返回字典
data = str2obj("[1, 2, 3]")        # 返回列表

# DataFrame 转换
df = str2df("data.csv")           # 支持 CSV
df = str2df("data.json")          # 支持 JSON
df = str2df("data.xlsx")          # 支持 Excel
```

### AI 模型集成

```python
from zartist.clients.qwen_vl import QwenVLClient, QwenVLConfig

# 初始化客户端
config = QwenVLConfig(api_key="your_api_key")
client = QwenVLClient(config)

# 分析图像
response = client.analyze_image(image, "描述这张图片中的主要对象")
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest tests/test_utils/test_image_utils.py

# 显示详细输出
pytest -v
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证
