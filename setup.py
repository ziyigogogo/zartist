from setuptools import setup, find_packages

setup(
    name="zartist",
    version="0.1",
    author="ziyi.ai",
    description="A Python utility package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/zartist",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "certifi>=2025.1.31",
        "numpy>=2.2.3",
        "openpyxl>=3.1.5",
        "pandas>=2.2.3",
        "pillow>=11.1.0",
        "python-dateutil>=2.9.0",
        "regex>=2024.11.6",
        "requests>=2.32.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite="tests",
)
