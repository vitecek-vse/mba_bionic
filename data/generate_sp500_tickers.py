import pandas as pd

# Fetch S&P 500 tickers from Wikipedia
url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
tables = pd.read_html(url)
df = tables[0]

# Save only the Symbol column
df[['Symbol']].to_csv('data/sp500_tickers.csv', index=False)

print(f"Saved {len(df)} tickers to data/sp500_tickers.csv") 