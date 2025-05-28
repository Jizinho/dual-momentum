import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("📊 Dual Momentum Strategy")

tickers = {
    "SXR8.DE": "Actions US (SXR8)",
    "ACWX": "Actions Monde (ACWX)",
    "AGG": "Obligations CT (AGG)",
    "TLT": "Obligations LT (TLT)"
}

def get_price_nearest_date(data, target_date):
    try:
        available_dates = data.index
        available_dates = available_dates[available_dates <= target_date]
        if len(available_dates) == 0:
            return None
        closest_date = available_dates[-1]
        return data.loc[closest_date]['Close']
    except:
        return None

def calc_perf(ticker):
    data = yf.download(ticker, period="1y", interval="1d", progress=False)
    if data.empty:
        st.warning(f"Aucune donnée trouvée pour {ticker}")
        return None, None
    if 'Close' not in data.columns:
        st.warning(f"La colonne 'Close' est absente pour {ticker}")
        return None, None

    try:
        today = data.index[-1]
        price_today = data['Close'].iloc[-1]

        date_6m = today - timedelta(days=182)
        date_12m = today - timedelta(days=365)

        price_6m = get_price_nearest_date(data, date_6m)
        price_12m = get_price_nearest_date(data, date_12m)

        if price_6m is None or price_12m is None:
            return None, None

        perf_6m = (price_today - price_6m) / price_6m * 100
        perf_12m = (price_today - price_12m) / price_12m * 100

        return perf_6m, perf_12m
    except Exception as e:
        st.error(f"Erreur lors du calcul pour {ticker} : {e}")
        return None, None

results = {}

with st.spinner("📥 Récupération des données..."):
    for ticker, name in tickers.items():
        perf_6m, perf_12m = calc_perf(ticker)
        results[ticker] = {
            "name": name,
            "perf_6m": perf_6m,
            "perf_12m": perf_12m,
        }

import math

df_display = pd.DataFrame([
    {
        "Actif": r["name"],
        "Performance 6 mois (%)": f"{r['perf_6m']:.2f}" if r['perf_6m'] is not None and not math.isnan(r['perf_6m']) else "N/A",
        "Performance 12 mois (%)": f"{r['perf_12m']:.2f}" if r['perf_12m'] is not None and not math.isnan(r['perf_12m']) else "N/A",
    }
    for r in results.values()
])

st.subheader("📈 Performances des actifs")
st.table(df_display)

perf_actions = max(
    results.get("SXR8.DE", {}).get("perf_12m") or -999,
    results.get("ACWX", {}).get("perf_12m") or -999,
)
perf_oblig = max(
    results.get("AGG", {}).get("perf_12m") or -999,
    results.get("TLT", {}).get("perf_12m") or -999,
)

st.subheader("📌 Recommandation")
if perf_actions > perf_oblig:
    st.success("📈 Investir en actions (US ou Monde)")
else:
    st.success("📉 Investir en obligations (court ou long terme)")
