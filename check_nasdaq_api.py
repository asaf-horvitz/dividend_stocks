import urllib.request
import json

_NASDAQ_API_URL = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=5&offset=0&download=true"
_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

def check_api():
    headers = {"User-Agent": _USER_AGENT}
    req = urllib.request.Request(_NASDAQ_API_URL, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = response.read()
        json_data = json.loads(data)
        rows = json_data.get("data", {}).get("rows", [])
        if rows:
            print(json.dumps(rows[0], indent=2))
        else:
            print("No rows found.")

if __name__ == "__main__":
    check_api()
