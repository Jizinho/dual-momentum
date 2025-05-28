import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_1y_performance(ticker: str):
    today = datetime.today().date()
    one_year_ago = today - timedelta(days=365)

    # Télécharge les données étendues autour de la période cible pour avoir des données valides
    data = yf.download(ticker, start=(one_year_ago - timedelta(days=5)).strftime('%Y-%m-%d'),
                                end=(today + timedelta(days=1)).strftime('%Y-%m-%d'),
                                progress=False)

    if data.empty or "Close" not in data:
        return f"{ticker} : No data"

    data = data['Close'].dropna()

    # S'assurer que les dates sont des objets datetime.date
    data.index = pd.to_datetime(data.index).date

    # Trouver les dates les plus proches disponibles
    closest_past_date = min([d for d in data.index if d >= one_year_ago], default=None)
    closest_today_date = max([d for d in data.index if d <= today], default=None)

    if not closest_past_date or not closest_today_date:
        return f"{ticker} : Not enough data"

    start_price = data.loc[closest_past_date]
    end_price = data.loc[closest_today_date]

    performance = ((end_price - start_price) / start_price) * 100
    return f"{ticker.replace('.DE','')} : {performance:.2f} %"

def main():
    tickers = ["SXR8.DE", "ACWX", "AGG", "TLT"]
    for ticker in tickers:
        print(get_1y_performance(ticker))

if __name__ == "__main__":
    main()
