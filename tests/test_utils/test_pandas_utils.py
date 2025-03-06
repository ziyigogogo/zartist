import os
import pytest
import pandas as pd
import json
import tempfile

from zartist.utils.pandas_utils import str2df
from zartist.errors import StrParseError


@pytest.fixture
def sample_df():
    """Create a sample DataFrame"""
    return pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c']
    })


@pytest.fixture
def temp_csv(sample_df):
    """Create a temporary CSV file"""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as f:
        sample_df.to_csv(f.name, index=False)
        return f.name


@pytest.fixture
def temp_json(sample_df):
    """Create a temporary JSON file"""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w', encoding='utf-8') as f:
        sample_df.to_json(f.name)
        return f.name


@pytest.fixture
def temp_excel(sample_df):
    """Create a temporary Excel file"""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        sample_df.to_excel(f.name, index=False)
        return f.name


def test_str2df_csv(temp_csv):
    """Test str2df with CSV file"""
    df = str2df(temp_csv)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['A', 'B']
    assert len(df) == 3
    os.unlink(temp_csv)


def test_str2df_json(temp_json):
    """Test str2df with JSON file"""
    df = str2df(temp_json)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['A', 'B']
    assert len(df) == 3
    os.unlink(temp_json)


def test_str2df_excel(temp_excel):
    """Test str2df with Excel file"""
    df = str2df(temp_excel)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['A', 'B']
    assert len(df) == 3
    os.unlink(temp_excel)


def test_str2df_jsonl():
    """Test str2df with JSONL file"""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, mode='w', encoding='utf-8') as f:
        for i in range(3):
            json.dump({'A': i+1, 'B': chr(97+i)}, f)
            f.write('\n')
        temp_jsonl = f.name

    df = str2df(temp_jsonl)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['A', 'B']
    assert len(df) == 3
    os.unlink(temp_jsonl)


def test_str2df_invalid():
    """Test str2df with invalid inputs"""
    # Test with unsupported file extension
    with pytest.raises(StrParseError):
        str2df("file.txt")
    
    # Test with non-existent file
    with pytest.raises(StrParseError):
        str2df("nonexistent.csv")
    
    # Test with invalid file content
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        f.write("invalid,csv,content\nwith,wrong,format")
        temp_invalid = f.name
    
    df = str2df(temp_invalid)  # Should still work but might have unexpected format
    assert isinstance(df, pd.DataFrame)
    os.unlink(temp_invalid)
