import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Dual Momentum", page_icon="📈")
st.title("📊 Stratégie Dual Momentum (Version Fiable - ETF US)")

# 🎯 ETF 100 % compatibles yfinance (ETF US)
etfs = {
    'US': 'SPY',           # S&P 500 US
    'World': 'ACWX',       # Actions monde hors US
    'Bonds_CT': 'AGG',     # Obligations court terme
    'Bonds_LT': 'TLT',     # Obligations long terme
    'T-Bill': 'BIL'        # Trésor US court terme (remplace ^IRX)
}

# Dates
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Fonction de performance 12 mois
@st.cache_data
def get_12m_perf(ticker):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1mo")
        if 'Adj Close' not in df or df['Adj Close'].dropna().empty:
            return None
        data = df['Adj Close'].dropna()
        if len(data) < 2:
            return None
        perf = ((data[-1] / data[0]) - 1) * 100
        return round(perf, 2)
    except:
        return None

# Calcul des performances
performances = {name: get_12m_perf(ticker) for name, ticker in etfs.items()}
perf_df = pd.DataFrame.from_dict(performances, orient='index', columns=['Performance 12M (%)'])

# Logique Dual Momentum
result = "⚠️ Données insuffisantes"

if all(performances[k] is not None for k in ['US', 'World', 'Bonds_CT', 'Bonds_LT', 'T-Bill']):
    stocks_avg = (performances['US'] + performances['World']) / 2
    bonds_avg = (performances['Bonds_CT'] + performances['Bonds_LT']) / 2

    if bonds_avg > stocks_avg:
        result = 'AGG' if performances['Bonds_CT'] > performances['Bonds_LT'] else 'TLT'
    else:
        if performances['US'] > performances['World']:
            result = 'SPY' if performances['US'] > performances['T-Bill'] else 'BIL'
        else:
            result = 'ACWX' if performances['World'] > performances['T-Bill'] else 'BIL'

# Ajouter la décision au tableau
perf_df.loc['📌 Choix recommandé'] = [result]

# Affichage tableau
st.dataframe(perf_df)

# Résultat
if "⚠️" in result:
    st.warning("Certaines données sont manquantes ou inexploitables.")
else:
    st.success(f"✅ ETF recommandé pour ce mois : **{result}**")

# Optionnel : visualisation
with st.expander("📉 Graphiques des ETF (Adj Close mensuel)"):
    for name, ticker in etfs.items():
        st.subheader(f"{name} ({ticker})")
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval="1mo")
            if 'Adj Close' in df and not df['Adj Close'].dropna().empty:
                st.line_chart(df['Adj Close'])
            else:
                st.info("⛔ Données indisponibles ou vides pour ce ticker.")
        except Exception as e:
            st.error(f"Erreur lors du chargement de {ticker} : {e}")
