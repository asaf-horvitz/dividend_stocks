import dash
from dash import dash_table, html, Input, Output
import pandas as pd
import os
from datetime import datetime

# Constants
_DIVIDEND_SYMBOLS_FILE = "all_dividend_symbols.txt"
_ALL_SYMBOLS_FILE = "all_symbols.csv"
_DIVIDEND_STOCKS_DIR = "dividend_stocks"

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
    
    # Calculate Yearly Dividend and Tooltip
    current_year = datetime.now().year
    start_year = current_year - 5
    
    yearly_dividends = []
    tooltips = []
    
    for symbol in df["Symbol"]:
        file_path = os.path.join(_DIVIDEND_STOCKS_DIR, f"{symbol}.csv")
        if not os.path.exists(file_path):
            yearly_dividends.append("-")
            tooltips.append("")
            continue
            
        try:
            div_df = pd.read_csv(file_path)
            if div_df.empty or "Ex-Dividend Date" not in div_df.columns:
                yearly_dividends.append("-")
                tooltips.append("")
                continue
                
            # Parse dates
            div_df["Date"] = pd.to_datetime(div_df["Ex-Dividend Date"], format="%m/%d/%Y", errors='coerce')
            
            # Sort by date descending for tooltip
            div_df = div_df.sort_values("Date", ascending=False)
            
            # Generate Tooltip (Markdown Table)
            # We'll show Date and Amount
            # Limit to last 10 years to avoid huge tooltips
            tooltip_df = div_df[div_df["Date"].dt.year >= (current_year - 10)]
            
            tooltip_md = "| Date | Amount |\n|---|---|\n"
            for _, row in tooltip_df.iterrows():
                date_str = row["Date"].strftime("%Y-%m-%d") if pd.notnull(row["Date"]) else str(row["Ex-Dividend Date"])
                amount = str(row.get("Amount", ""))
                tooltip_md += f"| {date_str} | {amount} |\n"
            tooltips.append(tooltip_md)

            # Filter last 5 years for Yearly Dividend Calculation
            div_df_period = div_df[div_df["Date"].dt.year >= start_year]
            
            if div_df_period.empty:
                yearly_dividends.append("-")
                continue
                
            # Get unique years in the 5-year window
            unique_years = sorted(div_df_period["Date"].dt.year.unique())
            
            # Ignore companies with less than 2 years dividend data
            if len(unique_years) < 2:
                yearly_dividends.append("-")
                continue
                
            # Ignore first and last year in the calculation
            # We need at least 3 years to have something left after removing first and last
            if len(unique_years) < 3:
                yearly_dividends.append("-")
                continue
                
            years_to_include = unique_years[1:-1]
            
            # Filter data for included years
            div_df_calc = div_df_period[div_df_period["Date"].dt.year.isin(years_to_include)]
            
            # Count dividends per year
            counts = div_df_calc.groupby(div_df_calc["Date"].dt.year).size()
            
            # Check consistency
            unique_counts = counts.unique()
            if len(unique_counts) == 1:
                yearly_dividends.append(str(unique_counts[0]))
            else:
                yearly_dividends.append("-")
                
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            yearly_dividends.append("-")
            tooltips.append("")
            
    df["Yearly Dividend"] = yearly_dividends
    df["tooltip"] = tooltips

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
    return df[["Symbol", "Market Cap", "Market Cap Value", "Yearly Dividend", "tooltip"]]

app = dash.Dash(__name__)

df = load_data()

app.layout = html.Div([
    html.H1("Dividend Stocks"),
    html.H3(f"Total Stocks: {len(df)}"),
    dash_table.DataTable(
        id='table',
        columns=[
            {"name": "Symbol", "id": "Symbol"},
            {"name": "Yearly Dividend", "id": "Yearly Dividend"},
            {"name": "Market Cap (Billions)", "id": "Market Cap"}
        ],
        data=df.to_dict('records'),
        sort_action="custom",
        sort_mode="single",
        sort_by=[],
        page_action='none',  # Disable pagination to show all rows
        style_cell={
            'textAlign': 'left',
            'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
            'whiteSpace': 'normal'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        # Tooltip configuration
        tooltip_data=[
            {
                'Yearly Dividend': {'value': row['tooltip'], 'type': 'markdown'}
            } for row in df.to_dict('records')
        ],
        tooltip_duration=None, # Keep tooltip open while hovering
        css=[{
            'selector': '.dash-table-tooltip',
            'rule': 'background-color: white; font-family: monospace; min-width: 200px; z-index: 1000;'
        }],
        
        # Add virtual scrolling for better performance with many rows
        virtualization=True,
        fixed_rows={'headers': True},
        style_table={'height': '800px', 'overflowY': 'auto'}
    )
])

@app.callback(
    [Output('table', 'data'), Output('table', 'tooltip_data')],
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
    else:
        dff = df
            
    tooltip_data = [
        {
            'Yearly Dividend': {'value': row['tooltip'], 'type': 'markdown'}
        } for row in dff.to_dict('records')
    ]
    
    return dff.to_dict('records'), tooltip_data

if __name__ == '__main__':
    app.run(debug=True)
