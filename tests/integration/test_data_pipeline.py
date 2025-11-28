import pytest
import pandas as pd
import os
from datetime import datetime, timedelta
from data.loader import (
    get_project_root,
    load_data,
    get_stooq_data,
    download_and_save_data
)

def test_end_to_end_data_pipeline(test_data_dir, monkeypatch):
    """Test the entire data pipeline from downloading to loading"""
    # Mock the project root
    def mock_get_project_root():
        return str(test_data_dir)
    
    monkeypatch.setattr("data.loader.get_project_root", mock_get_project_root)
    
    # Test data
    tickers = ["AAPL", "GOOG"]
    start_date = "2020-01-01"
    end_date = "2020-01-10"
    
    # Step 1: Download data
    download_and_save_data(tickers=tickers, start=start_date, end=end_date)
    
    # Step 2: Load the saved data
    stock_data, metadata = load_data()
    
    # Verify the data
    assert isinstance(stock_data, pd.DataFrame)
    assert isinstance(metadata, pd.DataFrame)
    
    # Check stock data
    assert len(stock_data) > 0
    assert all(col in stock_data.columns for col in ['date', 'ticker', 'close'])
    assert all(ticker in stock_data['ticker'].unique() for ticker in tickers)
    
    # Check metadata
    assert len(metadata) == len(tickers)
    assert all(col in metadata.columns for col in ['ticker', 'sector', 'volatility', 'market_cap', 'tags'])
    assert all(ticker in metadata['ticker'].values for ticker in tickers)

def test_data_consistency(test_data_dir, monkeypatch):
    """Test that data remains consistent across multiple operations"""
    # Mock the project root
    def mock_get_project_root():
        return str(test_data_dir)
    
    monkeypatch.setattr("data.loader.get_project_root", mock_get_project_root)
    
    # First download
    download_and_save_data(tickers=["AAPL"], start="2020-01-01", end="2020-01-10")
    
    # Load first data
    first_stock_data, first_metadata = load_data()
    
    # Second download (should not duplicate data)
    download_and_save_data(tickers=["AAPL"], start="2020-01-01", end="2020-01-10")
    
    # Load second data
    second_stock_data, second_metadata = load_data()
    
    # Compare data
    pd.testing.assert_frame_equal(first_stock_data, second_stock_data)
    pd.testing.assert_frame_equal(first_metadata, second_metadata)

def test_multiple_tickers_handling(test_data_dir, monkeypatch):
    """Test handling of multiple tickers"""
    # Mock the project root
    def mock_get_project_root():
        return str(test_data_dir)
    
    monkeypatch.setattr("data.loader.get_project_root", mock_get_project_root)
    
    # Download data for multiple tickers
    tickers = ["AAPL", "GOOG", "MSFT"]
    download_and_save_data(tickers=tickers, start="2020-01-01", end="2020-01-10")
    
    # Load data
    stock_data, metadata = load_data()
    
    # Verify all tickers are present
    assert len(metadata) == len(tickers)
    assert set(metadata['ticker']) == set(tickers)
    
    # Verify stock data contains all tickers
    assert set(stock_data['ticker'].unique()) == set(tickers)
    
    # Verify each ticker has the same number of days
    days_per_ticker = stock_data.groupby('ticker').size()
    assert all(count == days_per_ticker.iloc[0] for count in days_per_ticker) 