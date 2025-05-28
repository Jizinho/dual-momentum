import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Dual Momentum", page_icon="📈")
st.title("📊 Stratégie Dual Momentum - Version Fiable (USA-based tickers)")

# Tickers fiables et accessibles par yfinance
etfs = {
    'S&P500 (SPY)': 'SPY',        # remplace SXR8
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT',
    'US03MY (BIL)': 'BIL'         # remplace ^IRX
}

# Période : 12 mois
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

@st.cache_data
def get_12m_perf(ticker):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1mo")
        if 'Adj Close' not in df.columns or df['Adj Close'].dropna().empty:
            return None
        data = df['Adj Close'].dropna()
        if len(data) < 2:
            return None
        perf = ((data[-1] / data[0]) - 1) * 100
        return round(perf, 2)
    except:
        return None

# Récupérer les performances
performances = {name: get_12m_perf(ticker) for name, ticker in etfs.items()}
perf_df = pd.DataFrame.from_dict(performances, orient='index', columns=['Performance 12M (%)'])

# Appliquer la stratégie
result = "⚠️ Données insuffisantes"

if all(perf is not None for perf in performances.values()):
    stocks_avg = (performances['S&P500 (SPY)'] + performances['ACWX']) / 2
    bonds_avg = (performances['AGG'] + performances['TLT']) / 2

    if bonds_avg > stocks_avg:
        result = 'AGG' if performances['AGG'] > performances['TLT'] else 'TLT'
    else:
        if performances['S&P500 (SPY)'] > performances['ACWX']:
            result = 'S&P500 (SPY)' if performances['S&P500 (SPY)'] > performances['US03MY (BIL)'] else 'US03MY (BIL)'
        else:
            result = 'ACWX' if performances['ACWX'] > performances['US03MY (BIL)'] else 'US03MY (BIL)'

# Ajouter le résultat final au tableau
perf_df.loc['📌 Choix recommandé'] = [result]

# Afficher le tableau
st.dataframe(perf_df)

if "⚠️" in result:
    st.warning("Certaines données sont manquantes ou inexploitables.")
else:
    st.success(f"✅ ETF recommandé pour ce mois : **{result}**")

# Graphiques des données brutes
with st.expander("🔍 Voir les données brutes"):
    for name, ticker in etfs.items():
        st.write(f"**{name}** ({ticker})")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval="1mo")
            if 'Adj Close' in df and not df['Adj Close'].dropna().empty:
                st.line_chart(df['Adj Close'])
            else:
                st.info("⛔ Données indisponibles.")
        except Exception as e:
            st.error(f"Erreur : {e}")
