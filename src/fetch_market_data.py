import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# The master list of your actual holdings + tracked tech stocks
TICKERS = [
    "MSFT", "CRWD", "AVGO", "GLE.PA", "NVDA", "AMZN", "AXON", "PANW", 
    "INTC", "NOW", "IREN", "GOOG", "MU", "SOFI", "PLTR", "RDW", "DRAM"
]

def fetch_stock_data(tickers, period="1mo"):
    print(f"Fetching market data for the past {period}...")
    
    # Create the 'data/raw' folder if it doesn't exist
    os.makedirs("data/raw", exist_ok=True)
    
    # Process each ticker one by one to avoid SQLite lock errors
    for ticker in tickers:
        try:
            print(f"Downloading {ticker}...")
            # Download a single ticker at a time
            df = yf.download(ticker, period=period, progress=False)
            
            # Check if dataframe is empty
            if not df.empty:
                file_path = f"data/raw/{ticker}_raw_{datetime.now().strftime('%Y%m%d')}.csv"
                df.to_csv(file_path)
                print(f"  -> Successfully saved to {file_path}")
            else:
                print(f"  -> Warning: No data found for {ticker}")
                
        except Exception as e:
            print(f"  -> Failed to process {ticker}. Error: {e}")

if __name__ == "__main__":
    fetch_stock_data(TICKERS)
