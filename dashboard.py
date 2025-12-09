import dash
from dash import dash_table, html, Input, Output
import pandas as pd
import os

# Constants
_DIVIDEND_SYMBOLS_FILE = "all_dividend_symbols.txt"
_ALL_SYMBOLS_FILE = "all_symbols.csv"

def load_data():
    """Loads and processes stock data."""
    # Read dividend symbols
    if not os.path.exists(_DIVIDEND_SYMBOLS_FILE):
        return pd.DataFrame()
    
    with open(_DIVIDEND_SYMBOLS_FILE, "r") as f:
        dividend_symbols = set(line.strip() for line in f if line.strip())

    # Read all symbols data
    if not os.path.exists(_ALL_SYMBOLS_FILE):
        return pd.DataFrame()

    df = pd.read_csv(_ALL_SYMBOLS_FILE)
    
    # Filter for dividend stocks
    df = df[df["Symbol"].isin(dividend_symbols)].copy()
    
    # Format Market Cap
    def format_market_cap(val):
        try:
            val = float(val)
            # Format as Billions, integer, no suffix
            return f"{val / 1_000_000_000:.0f}"
        except (ValueError, TypeError):
            return val

    # Create a numeric column for sorting
    df["Market Cap Value"] = pd.to_numeric(df["Market Cap"], errors='coerce')
    
    # Format the display column
    df["Market Cap"] = df["Market Cap Value"].apply(format_market_cap)
    
    print(f"Loaded {len(df)} stocks.")
    return df[["Symbol", "Market Cap", "Market Cap Value"]]

app = dash.Dash(__name__)

df = load_data()

app.layout = html.Div([
    html.H1("Dividend Stocks"),
    html.H3(f"Total Stocks: {len(df)}"),
    dash_table.DataTable(
        id='table',
        columns=[
            {"name": "Symbol", "id": "Symbol"},
            {"name": "Market Cap (Billions)", "id": "Market Cap"}
        ],
        data=df.to_dict('records'),
        sort_action="custom",
        sort_mode="single",
        sort_by=[],
        page_action='none',  # Disable pagination to show all rows
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        # Add virtual scrolling for better performance with many rows
        virtualization=True,
        fixed_rows={'headers': True},
        style_table={'height': '800px', 'overflowY': 'auto'}
    )
])

@app.callback(
    Output('table', 'data'),
    Input('table', 'sort_by')
)
def update_table(sort_by):
    if len(sort_by):
        col = sort_by[0]['column_id']
        descending = sort_by[0]['direction'] == 'desc'
        
        if col == 'Market Cap':
            # Sort by the hidden Value column
            dff = df.sort_values('Market Cap Value', ascending=not descending)
        else:
            dff = df.sort_values(col, ascending=not descending)
            
        return dff.to_dict('records')
    
    return df.to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)
