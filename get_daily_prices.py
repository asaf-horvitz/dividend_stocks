import os
import time
import concurrent.futures
import yfinance as yf
from datetime import datetime, timedelta

# Constants
_INPUT_FILE = "all_dividend_symbols.txt"
_OUTPUT_DIR = "daily_stocks_price"
_MAX_WORKERS = 1
_YEARS_HISTORY = "15y"

def _get_symbols() -> list[str]:
    """Reads symbols from the input file."""
    if not os.path.exists(_INPUT_FILE):
        print(f"Error: {_INPUT_FILE} not found.")
        return []
    
    with open(_INPUT_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def _fetch_prices(symbol: str) -> None:
    """Fetches daily prices for a symbol using yfinance and saves to CSV."""
    output_path = os.path.join(_OUTPUT_DIR, f"{symbol}.csv")
    
    try:
        # Fetch history
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=_YEARS_HISTORY)
        
        if hist.empty:
            print(f"Warning: No data found for {symbol}")
            return

        # Select required columns: Low, High, Close, Volume
        hist = hist[["Low", "High", "Close", "Volume"]]
        
        # Remove time from index (keep only date)
        hist.index = hist.index.date
        
        # Round to 3 decimal places
        hist = hist.round(3)
        
        # Save to CSV
        hist.to_csv(output_path)
        
    except Exception as e:
        print(f"Error processing {symbol}: {e}")

def get_daily_prices() -> None:
    """Main function to fetch daily prices in parallel."""
    if not os.path.exists(_OUTPUT_DIR):
        os.makedirs(_OUTPUT_DIR)
        
    symbols = _get_symbols()
    print(f"Fetching daily prices for {len(symbols)} symbols...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = [executor.submit(_fetch_prices, symbol) for symbol in symbols]
        concurrent.futures.wait(futures)
        
    print("Finished fetching daily prices.")

if __name__ == "__main__":
    get_daily_prices()
