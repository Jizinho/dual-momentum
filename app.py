import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Dual Momentum Simplifié", page_icon="📈")
st.title("📈 Stratégie Dual Momentum (Simplifiée)")

# ETF compatibles
etfs = {
    'SPY (US Stocks)': 'SPY',
    'ACWX (World ex-US)': 'ACWX',
    'BIL (T-Bills)': 'BIL'
}

# Dates
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Fonction de perf
def get_perf(ticker):
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval="1mo")['Adj Close'].dropna()
        if len(data) < 2:
            return None
        return round((data[-1] / data[0] - 1) * 100, 2)
    except:
        return None

# Récupération
performances = {name: get_perf(ticker) for name, ticker in etfs.items()}
df = pd.DataFrame.from_dict(performances, orient='index', columns=['Perf 12 mois (%)'])

# Décision simple
decision = None
if all(v is not None for v in performances.values()):
    if performances['SPY (US Stocks)'] > performances['ACWX (World ex-US)']:
        decision = 'SPY' if performances['SPY (US Stocks)'] > performances['BIL (T-Bills)'] else 'BIL'
    else:
        decision = 'ACWX' if performances['ACWX (World ex-US)'] > performances['BIL (T-Bills)'] else 'BIL'

# Affichage
st.subheader("📊 Performances des 12 derniers mois")
st.dataframe(df)

if decision:
    st.success(f"📌 ETF recommandé : **{decision}**")
else:
    st.warning("Données insuffisantes pour prendre une décision.")
