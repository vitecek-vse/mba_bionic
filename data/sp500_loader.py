import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
from pathlib import Path
import os

def get_sp500_tickers():
    """Get list of S&P 500 tickers from a local CSV file"""
    csv_path = 'data/sp500_tickers.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} not found. Please run data/generate_sp500_tickers.py to generate it.")
    return pd.read_csv(csv_path)['Symbol'].tolist()

def get_stock_metadata(ticker):
    """Get detailed metadata for a stock using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get company name
        name = info.get('shortName', 'N/A')
        # Get sector and industry
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        
        # Get market cap
        market_cap = info.get('marketCap', 0)
        
        # Calculate volatility (using 1-year of daily data)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        hist = stock.history(start=start_date, end=end_date)
        if not hist.empty:
            returns = hist['Close'].pct_change()
            volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
        else:
            volatility = 0.3  # Default value if no data available
        
        # Create tags based on sector and industry
        tags = f"{sector}, {industry}"
        
        return {
            'ticker': ticker,
            'name': name,
            'sector': sector,
            'industry': industry,
            'volatility': volatility,
            'market_cap': market_cap,
            'tags': tags
        }
    except Exception as e:
        print(f"Error getting metadata for {ticker}: {str(e)}")
        return None

def update_sp500_metadata():
    """Update metadata for all S&P 500 stocks"""
    print("Fetching S&P 500 tickers...")
    tickers = get_sp500_tickers()
    
    # Load existing metadata if available
    project_root = Path(__file__).parent.parent
    metadata_path = project_root / "data" / "stock_metadata.csv"
    
    try:
        existing_metadata = pd.read_csv(metadata_path)
        existing_tickers = set(existing_metadata['ticker'])
    except FileNotFoundError:
        existing_metadata = pd.DataFrame()
        existing_tickers = set()
    
    # Prepare for new metadata
    new_metadata_rows = []
    
    print(f"Processing {len(tickers)} stocks...")
    for i, ticker in enumerate(tickers, 1):
        if ticker in existing_tickers:
            print(f"[{i}/{len(tickers)}] Skipping {ticker} - already exists")
            continue
            
        print(f"[{i}/{len(tickers)}] Processing {ticker}...")
        metadata = get_stock_metadata(ticker)
        
        if metadata:
            new_metadata_rows.append(metadata)
            print(f"✓ Added metadata for {ticker}")
        
        # Add delay to avoid rate limiting
        time.sleep(1)
    
    if new_metadata_rows:
        # Create new metadata DataFrame
        new_metadata = pd.DataFrame(new_metadata_rows)
        
        # Combine with existing metadata
        combined_metadata = pd.concat([existing_metadata, new_metadata], ignore_index=True)
        
        # Save to CSV
        combined_metadata.to_csv(metadata_path, index=False)
        print(f"\n✅ Successfully updated metadata for {len(new_metadata_rows)} stocks")
        print(f"Total stocks in metadata: {len(combined_metadata)}")
    else:
        print("\nℹ️ No new metadata to add")

if __name__ == "__main__":
    update_sp500_metadata() 