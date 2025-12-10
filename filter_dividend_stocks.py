import os

# Constants
_DIVIDEND_DIR = "dividend_stocks"
_OUTPUT_FILE = "all_dividend_symbols.txt"

def filter_dividend_stocks() -> None:
    """
    Filters dividend stock files.
    - Adds symbols with dividend data to all_dividend_symbols.txt.
    - Deletes files with no dividend data.
    """
    if not os.path.exists(_DIVIDEND_DIR):
        print(f"Directory {_DIVIDEND_DIR} does not exist.")
        return

    dividend_symbols = []
    files_to_remove = []

    print("Filtering dividend files...")
    for filename in os.listdir(_DIVIDEND_DIR):
        if not filename.endswith(".csv"):
            continue

        filepath = os.path.join(_DIVIDEND_DIR, filename)
        symbol = os.path.splitext(filename)[0]

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
                # Check if there is more than just the header
                if len(lines) > 1:
                    dividend_symbols.append(symbol)
                else:
                    files_to_remove.append(filepath)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    # Load sectors from all_symbols.csv
    symbol_sectors = {}
    try:
        import csv
        with open("all_symbols.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol_sectors[row["Symbol"]] = row.get("Sector", "Unknown")
    except Exception as e:
        print(f"Error reading all_symbols.csv: {e}")

    # Write symbols and sectors to file
    try:
        with open(_OUTPUT_FILE, "w") as f:
            for symbol in sorted(dividend_symbols):
                sector = symbol_sectors.get(symbol, "Unknown")
                f.write(f"{symbol},{sector}\n")
        print(f"Successfully wrote {len(dividend_symbols)} symbols to {_OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing to {_OUTPUT_FILE}: {e}")

    # Remove empty files
    for filepath in files_to_remove:
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error removing {filepath}: {e}")
    print(f"Removed {len(files_to_remove)} files with no dividend data.")

if __name__ == "__main__":
    filter_dividend_stocks()
