import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import timedelta
import math

st.title("📊 Dual Momentum Strategy")

tickers = {
    "SXR8.DE": "Actions US (SXR8)",
    "ACWX": "Actions Monde (ACWX)",
    "AGG": "Obligations CT (AGG)",
    "TLT": "Obligations LT (TLT)"
}

def calc_perf(ticker):
    data = yf.download(ticker, period="1y", interval="1d", progress=False)
    if data.empty or 'Close' not in data.columns:
        return None, None, data

    today = data.index[-1]

    date_6m = today - timedelta(days=182)
    date_12m = today - timedelta(days=365)

    # Trouver le dernier prix <= date_6m et date_12m
    price_6m_series = data[data.index <= date_6m]['Close']
    price_12m_series = data[data.index <= date_12m]['Close']

    if price_6m_series.empty or price_12m_series.empty:
        return None, None, data

    price_6m = price_6m_series.iloc[-1]
    price_12m = price_12m_series.iloc[-1]
    price_today = data['Close'][-1]

    perf_6m = (price_today - price_6m) / price_6m * 100
    perf_12m = (price_today - price_12m) / price_12m * 100

    return perf_6m, perf_12m, data

results = {}

with st.spinner("Récupération des données..."):
    for ticker, name in tickers.items():
        perf_6m, perf_12m, data = calc_perf(ticker)
        results[ticker] = {
            "name": name,
            "perf_6m": perf_6m,
            "perf_12m": perf_12m,
            "data": data
        }

# Affichage données brutes pour debug (tu peux commenter après)
for ticker, res in results.items():
    st.subheader(f"Données brutes pour {res['name']} ({ticker})")
    st.write(res["data"].tail(5))

# Préparation DataFrame pour affichage
def format_perf(p):
    if p is None or (isinstance(p, float) and math.isnan(p)):
        return "N/A"
    else:
        return f"{p:.2f}"

df_display = pd.DataFrame([
    {
        "Actif": r["name"],
        "Performance 6 mois (%)": format_perf(r['perf_6m']),
        "Performance 12 mois (%)": format_perf(r['perf_12m']),
    }
    for r in results.values()
])

st.subheader("Performances des actifs")
st.table(df_display)

# Dual Momentum simplifié
perf_actions = max(
    (results.get("SXR8.DE", {}).get("perf_12m") or -999),
    (results.get("ACWX", {}).get("perf_12m") or -999),
)
perf_oblig = max(
    (results.get("AGG", {}).get("perf_12m") or -999),
    (results.get("TLT", {}).get("perf_12m") or -999),
)

st.subheader("Recommandation")
if perf_actions > perf_oblig:
    st.success("📈 Investir en actions (US ou Monde)")
else:
    st.success("📉 Investir en obligations (court ou long terme)")
