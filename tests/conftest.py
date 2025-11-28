import pytest
import pandas as pd
import os
from datetime import datetime, timedelta
from data.loader import get_project_root

@pytest.fixture
def sample_stock_data():
    """Fixture providing sample stock price data"""
    dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='D')
    data = {
        'date': dates,
        'ticker': ['AAPL'] * len(dates),
        'close': [100.0 + i for i in range(len(dates))]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_metadata():
    """Fixture providing sample stock metadata"""
    data = {
        'ticker': ['AAPL', 'GOOG'],
        'sector': ['Technology', 'Technology'],
        'volatility': [0.2, 0.25],
        'market_cap': [1e9, 1.5e9],
        'tags': ['Tech', 'Tech']
    }
    return pd.DataFrame(data)

@pytest.fixture
def test_data_dir(tmp_path):
    """Fixture providing a temporary directory for test data"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def mock_stooq_response():
    """Fixture providing a mock response from Stooq API"""
    dates = pd.date_range(start='2020-01-01', end='2020-01-10', freq='D')
    data = {
        'Date': dates.strftime('%Y-%m-%d'),
        'Close': [100.0 + i for i in range(len(dates))]
    }
    return pd.DataFrame(data) 