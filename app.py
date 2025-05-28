import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_1y_performance(ticker: str):
    today = datetime.today().date()
    one_year_ago = today - timedelta(days=365)

    # Télécharger plus de données autour de la période cible
    data = yf.download(
        ticker,
        start=(one_year_ago - timedelta(days=10)).strftime('%Y-%m-%d'),
        end=(today + timedelta(days=1)).strftime('%Y-%m-%d'),
        progress=False
    )

    if data.empty or "Close" not in data:
        return f"{ticker.replace('.DE','')} : No data"

    close_prices = data["Close"].dropna()
    close_prices.index = pd.to_datetime(close_prices.index).date

    # Chercher les dates disponibles les plus proches
    past_dates = [d for d in close_prices.index if d >= one_year_ago]
    today_dates = [d for d in close_prices.index if d <= today]

    if not past_dates or not today_dates:
        return f"{ticker.replace('.DE','')} : Insufficient data"

    start_date = min(past_dates)
    end_date = max(today_dates)

    start_price = close_prices.get(start_date)
    end_price = close_prices.get(end_date)

    if start_price is None or end_price is None:
        return f"{ticker.replace('.DE','')} : Price data missing"

    try:
        performance = ((end_price - start_price) / start_price) * 100
        return f"{ticker.replace('.DE','')} : {performance:.2f} %"
    except ZeroDivisionError:
        return f"{ticker.replace('.DE','')} : Invalid start price (0)"

def main():
    tickers = ["SXR8.DE", "ACWX", "AGG", "TLT"]
    for ticker in tickers:
        print(get_1y_performance(ticker))

if __name__ == "__main__":
    main()
