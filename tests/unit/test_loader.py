import pytest
import pandas as pd
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from data.loader import (
    get_project_root,
    load_data,
    get_stooq_data,
    download_and_save_data
)

def test_get_project_root():
    """Test that get_project_root returns the correct path"""
    root = get_project_root()
    assert os.path.exists(root)
    assert os.path.isdir(root)
    assert os.path.exists(os.path.join(root, "data"))

def test_load_data(sample_stock_data, sample_metadata, test_data_dir, monkeypatch):
    """Test loading data from CSV files"""
    # Mock the project root to use our test directory
    def mock_get_project_root():
        return str(test_data_dir)
    
    monkeypatch.setattr("data.loader.get_project_root", mock_get_project_root)
    
    # Save sample data
    sample_stock_data.to_csv(os.path.join(test_data_dir, "data/stock_prices.csv"), index=False)
    sample_metadata.to_csv(os.path.join(test_data_dir, "data/stock_metadata.csv"), index=False)
    
    # Test loading
    stock_data, metadata = load_data()
    
    assert isinstance(stock_data, pd.DataFrame)
    assert isinstance(metadata, pd.DataFrame)
    assert len(stock_data) == len(sample_stock_data)
    assert len(metadata) == len(sample_metadata)
    assert all(col in stock_data.columns for col in ['date', 'ticker', 'close'])
    assert all(col in metadata.columns for col in ['ticker', 'sector', 'volatility', 'market_cap', 'tags'])

@patch('pandas.read_csv')
def test_get_stooq_data(mock_read_csv, mock_stooq_response):
    """Test getting data from Stooq"""
    mock_read_csv.return_value = mock_stooq_response
    
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2020, 1, 10)
    
    df, volatility = get_stooq_data("AAPL", start_date, end_date)
    
    assert isinstance(df, pd.DataFrame)
    assert isinstance(volatility, float)
    assert all(col in df.columns for col in ['date', 'ticker', 'close'])
    assert len(df) == len(mock_stooq_response)

def test_download_and_save_data(test_data_dir, monkeypatch):
    """Test downloading and saving data"""
    # Mock the project root
    def mock_get_project_root():
        return str(test_data_dir)
    
    monkeypatch.setattr("data.loader.get_project_root", mock_get_project_root)
    
    # Mock get_stooq_data to return sample data
    def mock_get_stooq_data(symbol, start_date, end_date):
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'ticker': [symbol] * len(dates),
            'close': [100.0 + i for i in range(len(dates))]
        })
        return df, 0.2
    
    monkeypatch.setattr("data.loader.get_stooq_data", mock_get_stooq_data)
    
    # Test downloading data
    download_and_save_data(tickers=["AAPL"], start="2020-01-01", end="2020-01-10")
    
    # Verify files were created
    assert os.path.exists(os.path.join(test_data_dir, "data/stock_prices.csv"))
    assert os.path.exists(os.path.join(test_data_dir, "data/stock_metadata.csv"))
    
    # Verify data was saved correctly
    stock_data = pd.read_csv(os.path.join(test_data_dir, "data/stock_prices.csv"))
    metadata = pd.read_csv(os.path.join(test_data_dir, "data/stock_metadata.csv"))
    
    assert len(stock_data) > 0
    assert len(metadata) > 0
    assert "AAPL" in metadata["ticker"].values 