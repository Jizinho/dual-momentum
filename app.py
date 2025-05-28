import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("📊 Dual Momentum Strategy")

# Définition des tickers et noms
tickers = {
    "SXR8.DE": "Actions US (SXR8)",
    "ACWX": "Actions Monde (ACWX)",
    "AGG": "Obligations CT (AGG)",
    "TLT": "Obligations LT (TLT)",
    "^IRX": "T-Bills (US03MY)"
}

# Fonction pour calculer performance sur 6M et 12M
def calc_perf(ticker):
    data = yf.download(ticker, period="1y", interval="1d", progress=False)
    if data.empty:
        return None, None
    today = data.index[-1]
    price_today = data['Close'][-1]

    date_6m = today - timedelta(days=182)
    date_12m = today - timedelta(days=365)

    # prix au plus proche date 6 mois
    price_6m = data['Close'].asof(date_6m)
    # prix au plus proche date 12 mois
    price_12m = data['Close'].asof(date_12m)

    perf_6m = (price_today - price_6m) / price_6m * 100 if price_6m else None
    perf_12m = (price_today - price_12m) / price_12m * 100 if price_12m else None

    return perf_6m, perf_12m

results = {}

with st.spinner("Récupération des données..."):
    for ticker, name in tickers.items():
        perf_6m, perf_12m = calc_perf(ticker)
        results[ticker] = {
            "name": name,
            "perf_6m": perf_6m,
            "perf_12m": perf_12m,
        }

# Affichage des résultats
st.subheader("Performances des actifs")

df_display = pd.DataFrame([
    {
        "Actif": r["name"],
        "Performance 6 mois (%)": f"{r['perf_6m']:.2f}" if r['perf_6m'] else "N/A",
        "Performance 12 mois (%)": f"{r['perf_12m']:.2f}" if r['perf_12m'] else "N/A",
    }
    for r in results.values()
])

st.table(df_display)

# Calcul recommandation Dual Momentum

def get_perf(ticker):
    val = results.get(ticker, {})
    return val.get("perf_12m") or -999

perf_actions = max(get_perf("SXR8.DE"), get_perf("ACWX"))
perf_oblig = max(get_perf("AGG"), get_perf("TLT"))
perf_tbills = get_perf("^IRX")

st.subheader("Recommandation")

if perf_actions > perf_oblig:
    if perf_actions > perf_tbills:
        st.success("📈 Investir en actions (US ou Monde)")
    else:
        st.info("💵 Rester en cash (T-Bills mieux que Actions)")
else:
    if perf_oblig > perf_tbills:
        st.success("📉 Investir en obligations (court ou long terme)")
    else:
        st.info("💵 Rester en cash (T-Bills mieux que Obligations)")

