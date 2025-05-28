import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Dual Momentum", page_icon="📈")
st.title("📊 Stratégie Dual Momentum - Automatisée")

# Définir les ETF et indices
etfs = {
    'SXR8': 'SXR8.DE',     # S&P500 version Europe (iShares)
    'ACWX': 'ACWX',        # Marchés mondiaux hors USA
    'AGG': 'AGG',          # Obligations US court terme
    'TLT': 'TLT',          # Obligations US long terme
    'US03MY': '^IRX'       # Taux du Trésor 3 mois
}

# Période : 12 mois en arrière depuis aujourd’hui
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Fonction de calcul de performance
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

# Calculer les performances des 12 derniers mois
performances = {name: get_12m_perf(ticker) for name, ticker in etfs.items()}

# Afficher les performances dans un tableau
perf_df = pd.DataFrame.from_dict(performances, orient='index', columns=['Performance 12M (%)'])

# Appliquer la stratégie Dual Momentum
result = "⚠️ Données insuffisantes"

if all(performances[k] is not None for k in ['SXR8', 'ACWX', 'AGG', 'TLT', 'US03MY']):
    stocks_avg = (performances['SXR8'] + performances['ACWX']) / 2
    bonds_avg = (performances['AGG'] + performances['TLT']) / 2

    if bonds_avg > stocks_avg:
        result = 'AGG' if performances['AGG'] > performances['TLT'] else 'TLT'
    else:
        if performances['SXR8'] > performances['ACWX']:
            result = 'SXR8' if performances['SXR8'] > performances['US03MY'] else 'US03MY'
        else:
            result = 'ACWX' if performances['ACWX'] > performances['US03MY'] else 'US03MY'

# Ajouter la ligne de résultat au tableau
perf_df.loc['📌 Choix recommandé'] = [result]

# Affichage
st.dataframe(perf_df)

if "⚠️" in result:
    st.warning("Certaines données sont manquantes. Vérifie les tickers ou réessaie plus tard.")
else:
    st.success(f"✅ ETF recommandé pour ce mois : **{result}**")

# Facultatif : afficher les données brutes (pour debug)
with st.expander("🔍 Voir les données brutes téléchargées"):
    for name, ticker in etfs.items():
        st.write(f"**{name}** ({ticker})")
        data = yf.download(ticker, start=start_date, end=end_date, interval="1mo")
        if 'Adj Close' in data and not data['Adj Close'].dropna().empty:
            st.line_chart(data['Adj Close'])
        else:
            st.info("⛔ Données indisponibles ou incompatibles pour ce ticker.")
