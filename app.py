import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.title("📊 Stratégie Dual Momentum - Automatisée")

# Définir les ETF
etfs = {
    'SXR8': 'SXR8.DE',     # S&P500 (Europe)
    'ACWX': 'ACWX',        # Monde hors US
    'AGG': 'AGG',          # Obligations CT US
    'TLT': 'TLT',          # Obligations LT US
    'US03MY': '^IRX'       # Rendement 3M (proxy)
}

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

@st.cache_data
def get_12m_perf(ticker):
    data = yf.download(ticker, start=start_date, end=end_date, interval="1mo")['Adj Close']
    if data.empty or len(data) < 2:
        return None
    perf = ((data[-1] / data[0]) - 1) * 100
    return round(perf, 2)

# Calculer performances
performances = {name: get_12m_perf(ticker) for name, ticker in etfs.items()}
perf_df = pd.DataFrame.from_dict(performances, orient='index', columns=['Performance 12M (%)'])

# Appliquer la stratégie
stocks_avg = (performances['SXR8'] + performances['ACWX']) / 2
bonds_avg = (performances['AGG'] + performances['TLT']) / 2

if bonds_avg > stocks_avg:
    result = 'AGG' if performances['AGG'] > performances['TLT'] else 'TLT'
else:
    if performances['SXR8'] > performances['ACWX']:
        result = 'SXR8' if performances['SXR8'] > performances['US03MY'] else 'US03MY'
    else:
        result = 'ACWX' if performances['ACWX'] > performances['US03MY'] else 'US03MY'

perf_df.loc['Résultat'] = [result]

st.dataframe(perf_df)
st.success(f"✅ ETF recommandé ce mois-ci : **{result}**")
