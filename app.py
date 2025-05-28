import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.title("Dual Momentum - Performances 6M & 12M")

# Tickers à analyser
tickers = {
    "S&P 500 (SPY)": "SPY",
    "ACWI ex-US (ACWX)": "ACWX",
    "US Bonds (AGG)": "AGG",
    "Long-Term Bonds (TLT)": "TLT",
    "US 3M T-Bill (IRX)": "^IRX"
}

# Dates de référence
today = datetime.today()
six_months_ago = today - timedelta(days=182)
twelve_months_ago = today - timedelta(days=365)

@st.cache_data
def calc_performance(ticker):
    data = yf.download(ticker, start=twelve_months_ago, end=today)
    if data.empty or "Close" not in data.columns:
        return None, None

    price_today = data["Close"][-1]
    
    price_6m_ago = data[data.index <= six_months_ago]["Close"]
    price_12m_ago = data[data.index <= twelve_months_ago]["Close"]

    if price_6m_ago.empty or price_12m_ago.empty:
        return None, None

    perf_6m = (price_today - price_6m_ago[-1]) / price_6m_ago[-1] * 100
    perf_12m = (price_today - price_12m_ago[-1]) / price_12m_ago[-1] * 100

    return round(perf_6m, 2), round(perf_12m, 2)

# Création du tableau de performance
results = []
for name, ticker in tickers.items():
    perf_6m, perf_12m = calc_performance(ticker)
    results.append({
        "Nom": name,
        "Ticker": ticker,
        "Perf. 6M (%)": perf_6m,
        "Perf. 12M (%)": perf_12m
    })

df = pd.DataFrame(results)
st.dataframe(df)
