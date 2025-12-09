import dash
from dash import dash_table, html, Input, Output
import pandas as pd
import os
from datetime import datetime

# Constants
_DIVIDEND_SYMBOLS_FILE = "all_dividend_symbols.txt"
_ALL_SYMBOLS_FILE = "all_symbols.csv"
_DIVIDEND_STOCKS_DIR = "dividend_stocks"

def _load_dividend_symbols():
    """Loads dividend symbols from file."""
    if not os.path.exists(_DIVIDEND_SYMBOLS_FILE):
        return set()
    with open(_DIVIDEND_SYMBOLS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def _load_all_symbols():
    """Loads all stock symbols from CSV."""
    if not os.path.exists(_ALL_SYMBOLS_FILE):
        return pd.DataFrame()
    return pd.read_csv(_ALL_SYMBOLS_FILE)

def _get_dividend_data(symbol):
    """Reads dividend data for a symbol."""
    file_path = os.path.join(_DIVIDEND_STOCKS_DIR, f"{symbol}.csv")
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        if df.empty or "Ex-Dividend Date" not in df.columns:
            return pd.DataFrame()
        
        df["Date"] = pd.to_datetime(df["Ex-Dividend Date"], format="%m/%d/%Y", errors='coerce')
        return df
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return pd.DataFrame()

def _generate_tooltip(div_df):
    """Generates a markdown tooltip for dividend history."""
    if div_df.empty:
        return ""
    
    # Limit to last 10 years
    current_year = datetime.now().year
    tooltip_df = div_df[div_df["Date"].dt.year >= (current_year - 10)]
    tooltip_df = tooltip_df.sort_values("Date", ascending=False)
    
    tooltip_md = "| Date | Amount |\n|---|---|\n"
    for _, row in tooltip_df.iterrows():
        date_str = row["Date"].strftime("%Y-%m-%d") if pd.notnull(row["Date"]) else str(row["Ex-Dividend Date"])
        amount = str(row.get("Amount", ""))
        tooltip_md += f"| {date_str} | {amount} |\n"
    return tooltip_md

def _calculate_yearly_dividend(div_df):
    """Calculates the consistent yearly dividend count."""
    if div_df.empty:
        return "-"
    
    current_year = datetime.now().year
    start_year = current_year - 5
    
    # Filter last 5 years
    div_df_period = div_df[div_df["Date"].dt.year >= start_year]
    if div_df_period.empty:
        return "-"
        
    unique_years = sorted(div_df_period["Date"].dt.year.unique())
    
    if len(unique_years) < 2: # Need at least 2 years of data
        return "-"
    if len(unique_years) < 3: # Need 3 years to drop first/last
        return "-"
        
    years_to_include = unique_years[1:-1]
    div_df_calc = div_df_period[div_df_period["Date"].dt.year.isin(years_to_include)]
    
    counts = div_df_calc.groupby(div_df_calc["Date"].dt.year).size()
    unique_counts = counts.unique()
    
    return str(unique_counts[0]) if len(unique_counts) == 1 else "-"

def _format_market_cap(val):
    """Formats market cap to Billions."""
    try:
        val = float(val)
        return f"{val / 1_000_000_000:.0f}"
    except (ValueError, TypeError):
        return val

def load_data():
    """Main function to load and process stock data."""
    dividend_symbols = _load_dividend_symbols()
    df = _load_all_symbols()
    
    if df.empty or not dividend_symbols:
        return pd.DataFrame()
        
    df = df[df["Symbol"].isin(dividend_symbols)].copy()
    
    yearly_dividends = []
    tooltips = []
    
    for symbol in df["Symbol"]:
        div_df = _get_dividend_data(symbol)
        tooltips.append(_generate_tooltip(div_df))
        yearly_dividends.append(_calculate_yearly_dividend(div_df))
            
    df["Yearly Dividend"] = yearly_dividends
    df["tooltip"] = tooltips
    df["Market Cap Value"] = pd.to_numeric(df["Market Cap"], errors='coerce')
    df["Market Cap"] = df["Market Cap Value"].apply(_format_market_cap)
    
    print(f"Loaded {len(df)} stocks.")
    return df[["Symbol", "Market Cap", "Market Cap Value", "Yearly Dividend", "tooltip"]]

app = dash.Dash(__name__)

df = load_data()

app.layout = html.Div([
    html.Div([
        html.H1("Dividend Stocks Summary", style={'margin': '0', 'marginRight': '20px', 'lineHeight': '60px'}),
        html.H3(f"Total Stocks: {len(df)}", style={'margin': '0', 'lineHeight': '60px'})
    ], style={'height': '60px', 'padding': '0 20px', 'display': 'flex', 'alignItems': 'center', 'backgroundColor': '#f9f9f9', 'borderBottom': '1px solid #ddd'}),
    html.Div([
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
            page_action='none',
            style_cell={
                'textAlign': 'left',
                'width': '33%',
                'minWidth': '100px',
                'maxWidth': '500px',
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
            tooltip_data=[
                {'Yearly Dividend': {'value': row['tooltip'], 'type': 'markdown'}} 
                for row in df.to_dict('records')
            ],
            tooltip_duration=None,
            css=[{
                'selector': '.dash-table-tooltip',
                'rule': '''
                    background-color: white;
                    font-family: monospace;
                    min-width: 200px;
                    z-index: 1000;
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    border: 1px solid #ccc;
                    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                '''
            }],
            virtualization=True,
            fixed_rows={'headers': True},
            style_table={'height': 'calc(100vh - 70px)', 'maxHeight': 'calc(100vh - 70px)', 'overflowY': 'auto'}
        )
    ])
], style={'height': '100vh', 'overflow': 'hidden'})

@app.callback(
    [Output('table', 'data'), Output('table', 'tooltip_data')],
    Input('table', 'sort_by')
)
def update_table(sort_by):
    dff = df
    if len(sort_by):
        col = sort_by[0]['column_id']
        descending = sort_by[0]['direction'] == 'desc'
        if col == 'Market Cap':
            dff = df.sort_values('Market Cap Value', ascending=not descending)
        else:
            dff = df.sort_values(col, ascending=not descending)
            
    tooltip_data = [
        {'Yearly Dividend': {'value': row['tooltip'], 'type': 'markdown'}} 
        for row in dff.to_dict('records')
    ]
    return dff.to_dict('records'), tooltip_data

if __name__ == '__main__':
    app.run(debug=True)
