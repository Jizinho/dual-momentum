import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import timedelta

st.set_page_config(page_title="Dual Momentum", layout="centered")
st.title("📊 Dual Momentum Strategy")

# Liste des actifs
tickers = {
    "SXR8.DE": "Actions US (SXR8)",
    "ACWX": "Actions Monde (ACWX)",
    "AGG": "Obligations CT (AGG)",
    "TLT": "Obligations LT (TLT)"
}

# Fonction pour calculer les performances
def calc_perf(ticker):
    data = yf.download(ticker, period="1y", interval="1d", progress=False)

    if data.empty or 'Close' not in data.columns:
        return None, None

    data = data[['Close']].dropna()
    if data.empty:
        return None, None

    today = data.index[-1]
    price_today = data['Close'].iloc[-1]

    date_6m = today - timedelta(days=182)
    date_12m = today - timedelta(days=365)

    price_6m_series = data[data.index <= date_6m]['Close']
    price_12m_series = data[data.index <= date_12m]['Close']

    if price_6m_series.empty or price_12m_series.empty:
        return None, None

    price_6m = price_6m_series.iloc[-1]
    price_12m = price_12m_series.iloc[-1]

    perf_6m = (price_today - price_6m) / price_6m * 100
    perf_12m = (price_today - price_12m) / price_12m * 100

    return perf_6m, perf_12m

# Chargement des données
results = {}
with st.spinner("📥 Récupération des données..."):
    for ticker, name in tickers.items():
        perf_6m, perf_12m = calc_perf(ticker)
        results[ticker] = {
            "name": name,
            "perf_6m": perf_6m,
            "perf_12m": perf_12m,
        }

# Affichage du tableau
df_display = pd.DataFrame([
    {
        "Actif": r["name"],
        "Performance 6 mois (%)": f"{r['perf_6m']:.2f}" if isinstance(r['perf_6m'], (float, int)) else "N/A",
        "Performance 12 mois (%)": f"{r['perf_12m']:.2f}" if isinstance(r['perf_12m'], (float, int)) else "N/A",
    }
    for r in results.values()
])

st.subheader("📈 Performances des actifs")
st.table(df_display)

# Recommandation
def safe_perf(val):
    return val if isinstance(val, (float, int)) and pd.notna(val) else -999

perf_actions = max(
    safe_perf(results.get("SXR8.DE", {}).get("perf_12m")),
    safe_perf(results.get("ACWX", {}).get("perf_12m")),
)

perf_oblig = max(
    safe_perf(results.get("AGG", {}).get("perf_12m")),
    safe_perf(results.get("TLT", {}).get("perf_12m")),
)

st.subheader("🔍 Recommandation")
if perf_actions > perf_oblig:
    st.success("📈 Investir en actions (US ou Monde)")
else:
    st.info("📉 Investir en obligations (court ou long terme)")
