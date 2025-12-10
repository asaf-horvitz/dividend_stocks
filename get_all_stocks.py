import csv
import json
import urllib.request
from typing import List, Dict, Any

# Constants
_NASDAQ_API_URL = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true"
_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
_OUTPUT_FILENAME = "all_symbols.csv"
_MIN_MARKET_CAP = 1_000_000_000

def _fetch_stock_data() -> Dict[str, Any]:
    """Fetches stock data from the NASDAQ API."""
    headers = {"User-Agent": _USER_AGENT}
    req = urllib.request.Request(_NASDAQ_API_URL, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = response.read()
        return json.loads(data)

def _parse_market_cap(market_cap_str: str) -> float:
    """Parses market cap string to float."""
    if not market_cap_str:
        return 0.0
    try:
        # Remove commas and currency symbols if present
        clean_str = market_cap_str.replace(",", "").replace("$", "")
        return float(clean_str)
    except ValueError:
        return 0.0

def _extract_symbols(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extracts symbol, market cap, and sector from the API response, filtering by market cap."""
    rows = data.get("data", {}).get("rows", [])
    extracted_data = []
    for row in rows:
        symbol = row.get("symbol")
        market_cap_str = row.get("marketCap")
        sector = row.get("sector", "Unknown")
        
        market_cap_val = _parse_market_cap(market_cap_str)
        
        if symbol and market_cap_val >= _MIN_MARKET_CAP:
             extracted_data.append({
                 "Symbol": symbol, 
                 "Market Cap": f"{market_cap_val:.2f}",
                 "Sector": sector
             })
    return extracted_data

def _write_to_csv(data: List[Dict[str, str]], filename: str) -> None:
    """Writes the extracted data to a CSV file."""
    if not data:
        print("No data to write.")
        return
    
    fieldnames = ["Symbol", "Market Cap", "Sector"]
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def get_all_stocks() -> None:
    """Main function to fetch and save stock symbols."""
    print("Fetching stock data...")
    try:
        data = _fetch_stock_data()
        extracted = _extract_symbols(data)
        _write_to_csv(extracted, _OUTPUT_FILENAME)
        print(f"Successfully saved {len(extracted)} symbols to {_OUTPUT_FILENAME}")
    except Exception as e:
        print(f"Error fetching stocks: {e}")

if __name__ == "__main__":
    get_all_stocks()
