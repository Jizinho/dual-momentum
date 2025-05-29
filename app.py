import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("📊 Dual Momentum Avancé")

# Tickers utilisés
tickers = {
    "SXR8.DE": "Actions US (SXR8)",
    "ACWX": "Actions Monde (ACWX)",
    "AGG": "Obligations CT (AGG)",
    "TLT": "Obligations LT (TLT)",
    "US03MY": "Bonds du Trésor 3 mois"
}

def calc_12m_perf(ticker):
    data = yf.download(ticker, period="13mo", interval="1d", progress=False)

    if data.empty:
        return None

    # Gérer les cas multi-index
    if 'Close' not in data.columns:
        if isinstance(data.columns, pd.MultiIndex):
            if (ticker, 'Close') in data.columns:
                data = data[(ticker, 'Close')].dropna().to_frame()
                data.columns = ['Close']
            else:
                return None
        else:
            return None

    data = data.dropna(subset=['Close'])

    if len(data) < 2:
        return None

    price_today = data['Close'][-1]
    date_12m = data.index[-1] - timedelta(days=365)

    price_12m = data['Close'].asof(date_12m)
    if pd.isna(price_12m) or price_12m == 0:
        return None

    perf = (price_today - price_12m) / price_12m * 100
    return perf

results = {}

with st.spinner("🔄 Récupération des données..."):
    for ticker in tickers:
        perf = calc_12m_perf(ticker)
        results[ticker] = perf

# Affichage des performances
st.subheader("📈 Performances sur 12 mois")
df_display = pd.DataFrame([
    {"Actif": tickers[ticker], "Performance 12 mois (%)": f"{perf:.2f}" if perf is not None else "N/A"}
    for ticker, perf in results.items()
])
st.table(df_display)

# 🧠 Logique avancée Dual Momentum
st.subheader("🤖 Recommandation finale")

def safe_val(val):
    return val if val is not None else -9999

actions_max = max(safe_val(results["SXR8.DE"]), safe_val(results["ACWX"]))
oblig_max = max(safe_val(results["AGG"]), safe_val(results["TLT"]))

if actions_max > oblig_max:
    st.info("📊 Les actions sont en tête")

    if safe_val(results["SXR8.DE"]) > safe_val(results["ACWX"]):
        st.write("🔍 Actions US battent le reste du monde")
        if safe_val(results["SXR8.DE"]) > safe_val(results["US03MY"]):
            st.success("✅ Choix final : Actions US (SXR8)")
        else:
            st.warning("⚠️ Aucune allocation claire, sécurité (bonds du Trésor) recommandée")
    else:
        st.write("🔍 Actions Monde battent les US")
        if safe_val(results["ACWX"]) > safe_val(results["US03MY"]):
            st.success("✅ Choix final : Actions Monde (ACWX)")
        else:
            st.warning("⚠️ Aucune allocation claire, sécurité (bonds du Trésor) recommandée")
else:
    st.info("📉 Les obligations sont en tête")

    if safe_val(results["AGG"]) > safe_val(results["TLT"]):
        st.success("✅ Choix final : Obligations CT (AGG)")
    else:
        st.success("✅ Choix final : Obligations LT (TLT)")
