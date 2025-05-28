import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("📊 Performance à 1 an des ETF")

# Liste des ETF
tickers = {
    "SXR8": "SXR8.DE",
    "ACWX": "ACWX",
    "AGG": "AGG",
    "TLT": "TLT"
}

@st.cache_data(ttl=3600)
def get_1y_performance(ticker_symbol):
    today = datetime.today().date()
    one_year_ago = today - timedelta(days=365)

    try:
        data = yf.download(
            ticker_symbol,
            start=(one_year_ago - timedelta(days=10)).strftime('%Y-%m-%d'),
            end=(today + timedelta(days=1)).strftime('%Y-%m-%d'),
            progress=False
        )

        if data.empty or "Close" not in data:
            return None

        close_prices = data["Close"].dropna()
        close_prices.index = pd.to_datetime(close_prices.index).date

        start_date = min([d for d in close_prices.index if d >= one_year_ago], default=None)
        end_date = max([d for d in close_prices.index if d <= today], default=None)

        if not start_date or not end_date:
            return None

        start_price = close_prices.get(start_date)
        end_price = close_prices.get(end_date)

        if start_price is None or end_price is None:
            return None

        performance = ((end_price - start_price) / start_price) * 100
        return round(performance, 2)
    except Exception as e:
        st.error(f"Erreur pour {ticker_symbol} : {str(e)}")
        return None

# Affichage
for label, symbol in tickers.items():
    perf = get_1y_performance(symbol)
    if perf is not None:
        st.markdown(f"**{label}** : {perf:+.2f} %")
    else:
        st.markdown(f"**{label}** : Données indisponibles ❌")
