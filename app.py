import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import math

st.title("📊 Dual Momentum Strategy (version stable)")

# Liste des tickers et leur description
tickers = {
    "AGG": "Obligations CT",
    "TLT": "Obligations LT",
    "SXR8.DE": "Actions US",
    "ACWX": "Actions Monde",
    "^IRX": "Bons du Trésor US 3M"
}

# Fonction pour calculer la performance sur 12 mois
def calc_12m_perf(ticker):
    data = yf.download(ticker, period="13mo", interval="1d", progress=False)
    if data.empty or 'Close' not in data.columns:
        return None

    data = data.dropna(subset=['Close'])
    data = data.sort_index()
    try:
        price_today = data['Close'].iloc[-1]
        date_12m = data.index[-1] - timedelta(days=365)
        price_12m = data['Close'].asof(date_12m)
        if pd.isna(price_12m):
            return None
        return (price_today - price_12m) / price_12m * 100
    except:
        return None

# Calcul des performances
results = {}
with st.spinner("🔄 Chargement des données..."):
    for ticker in tickers:
        perf = calc_12m_perf(ticker)
        results[ticker] = perf

# Affichage des résultats
st.subheader("📈 Performances sur 12 mois")
df = pd.DataFrame.from_dict(results, orient='index', columns=['Perf 12 mois (%)'])
df.index = [tickers[t] for t in df.index]

# Mise en forme
styled_df = df.style.format("{:.2f}").highlight_max(color='lightgreen')
st.dataframe(styled_df, use_container_width=True)

# Logique Dual Momentum
actions_max = max(results.get("SXR8.DE") or -999, results.get("ACWX") or -999)
oblig_max = max(results.get("AGG") or -999, results.get("TLT") or -999)
taux = results.get("^IRX") or -999

st.subheader("🤖 Recommandation")

if actions_max > oblig_max:
    if (results.get("SXR8.DE") or -999) > (results.get("ACWX") or -999):
        if (results.get("SXR8.DE") or -999) > taux:
            st.success("✅ Choisir : Actions US (SXR8)")
        else:
            st.success("✅ Choisir : Bons du Trésor US 3M")
    else:
        if (results.get("ACWX") or -999) > taux:
            st.success("✅ Choisir : Actions Monde (ACWX)")
        else:
            st.success("✅ Choisir : Bons du Trésor US 3M")
else:
    if (results.get("AGG") or -999) > (results.get("TLT") or -999):
        st.success("✅ Choisir : Obligations CT (AGG)")
    else:
        st.success("✅ Choisir : Obligations LT (TLT)")
