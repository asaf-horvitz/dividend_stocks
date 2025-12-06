import csv
import json
import os
import urllib.request
import concurrent.futures
from typing import List, Dict, Any

# Constants
_API_URL_TEMPLATE = "https://api.nasdaq.com/api/quote/{}/dividends?assetclass=stocks"
_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
_INPUT_FILENAME = "all_symbols.csv"
_OUTPUT_DIR = "dividend_stocks"
_MAX_WORKERS = 5

def _get_symbols() -> List[str]:
    """Reads symbols from the input CSV file."""
    symbols = []
    if not os.path.exists(_INPUT_FILENAME):
        print(f"Error: {_INPUT_FILENAME} not found.")
        return symbols
        
    with open(_INPUT_FILENAME, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "Symbol" in row:
                symbols.append(row["Symbol"])
    return symbols

def _fetch_dividend_data(symbol: str) -> List[Dict[str, str]]:
    """Fetches dividend data for a single symbol."""
    url = _API_URL_TEMPLATE.format(symbol)
    headers = {"User-Agent": _USER_AGENT}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return _extract_dividends(data)
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return []

def _extract_dividends(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extracts dividend information from the API response."""
    dividends = []
    if not data or "data" not in data or not data["data"]:
        return dividends
        
    dividend_data = data["data"].get("dividends", {})
    if not dividend_data:
        return dividends

    rows = dividend_data.get("rows", [])
    if not rows:
        return dividends

    for row in rows:
        dividends.append({
            "Ex-Dividend Date": row.get("exOrEffDate", "N/A"),
            "Type": row.get("type", "N/A"),
            "Amount": row.get("amount", "N/A"),
            "Declaration Date": row.get("declarationDate", "N/A"),
            "Record Date": row.get("recordDate", "N/A"),
            "Payment Date": row.get("paymentDate", "N/A"),
            "Currency": row.get("currency", "N/A")
        })
    return dividends

def _write_dividend_csv(symbol: str, dividends: List[Dict[str, str]]) -> None:
    """Writes dividend data to a CSV file."""
    filepath = os.path.join(_OUTPUT_DIR, f"{symbol}.csv")
    
    fieldnames = ["Ex-Dividend Date", "Type", "Amount", "Declaration Date", "Record Date", "Payment Date", "Currency"]
    
    try:
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if dividends:
                writer.writerows(dividends)
    except Exception as e:
        print(f"Error writing CSV for {symbol}: {e}")

def _process_stock(symbol: str) -> None:
    """Orchestrates fetching and writing for a single stock."""
    print(f"Processing {symbol}...")
    dividends = _fetch_dividend_data(symbol)
    _write_dividend_csv(symbol, dividends)

def get_dividend_stocks() -> None:
    """Main function to fetch dividend stocks in parallel."""
    if not os.path.exists(_OUTPUT_DIR):
        os.makedirs(_OUTPUT_DIR)
        
    symbols = _get_symbols()
    print(f"Found {len(symbols)} symbols to process.")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        executor.map(_process_stock, symbols)
    
    print("Finished processing all stocks.")

if __name__ == "__main__":
    get_dividend_stocks()
