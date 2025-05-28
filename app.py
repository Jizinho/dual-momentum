import yfinance as yf
import pandas as pd
from datetime import datetime

# List of tickers to analyze
tickers = ['SXR8.L', 'ACWX.L', 'AGG.L', 'TLT.L', 'US03MY.L']

# Get today's date and calculate start date (1 year ago)
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Download adjusted close prices for all tickers
data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

# Check if we have data for each ticker
valid_data = {}
for ticker in tickers:
    if ticker in data.columns:
        # Drop any NaN values and check if we have at least 2 data points
        series = data[ticker].dropna()
        if len(series) > 1:
            valid_data[ticker] = series
        else:
            print(f"Insufficient data for {ticker}. At least 2 data points needed.")
    else:
        print(f"Failed to retrieve data for {ticker}")

if valid_data:
    # Create DataFrame and sort by date
    valid_data = pd.DataFrame(valid_data).sort_index()
    
    # Calculate 12-month performance
    performance = (valid_data.iloc[-1] / valid_data.iloc[0] - 1) * 100
    
    print("\nPerformance des actifs sur 12 mois :")
    for ticker, perf in.items():
        print(f"{ticker}: {perf:.2f}%")
    
    # Apply Dual Momentum strategy
    try:
        bond_perf = max(performance['AGG.L'], performance['TLT.L'])
        stock_perf = max(performance['SXR8.L'], performance['ACWX.L'])
        
        result = "Résultat final : "
        if bond_perf > stock_perf:
            result += "AGG" if performance['AGG.L'] > performance['TLT.L'] else "TLT"
        else:
            if performance['SXR8.L'] > performance['ACWX.L']:
                result += "SXR8" if performance['SXR8.L'] > performance['US03MY.L'] else "US03MY"
            else:
                result += "ACWX" if performance['ACWX.L'] > performance['US03MY.L'] else "US03MY"
        
        print("\n" + result)
    
    except KeyError as e:
        print(f"Missing data for required ticker: {e}")
else:
    print("Error: No valid data retrieved for analysis. Please check your internet connection and ticker symbols.")
