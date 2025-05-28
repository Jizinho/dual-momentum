import yfinance as yf
from datetime import datetime, timedelta

def get_1y_performance(ticker: str):
    today = datetime.today()
    one_year_ago = today - timedelta(days=365)

    # Télécharger les données des 2 jours (pour éviter les jours fériés/weekends)
    data = yf.download(ticker, start=one_year_ago.strftime('%Y-%m-%d'), end=today.strftime('%Y-%m-%d'))
    
    if data.empty or "Close" not in data:
        return f"{ticker} : No data"

    # Utiliser la première et la dernière valeur de clôture disponibles
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]

    performance = ((end_price - start_price) / start_price) * 100
    return f"{ticker.replace('.DE','')} : {performance:.2f} %"

def main():
    tickers = ["SXR8.DE", "ACWX", "AGG", "TLT"]
    for ticker in tickers:
        print(get_1y_performance(ticker))

if __name__ == "__main__":
    main()
