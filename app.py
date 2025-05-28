import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime

# Tickers et alias simples
tickers = {
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT',
    'US03MY': '^IRX'  # Taux 3 mois
}

# Dates d’analyse
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Téléchargement brut
raw_data = yf.download(list(tickers.values()), start=start_date, end=end_date)

# Extraction de la colonne 'Adj Close' avec renommage
data = raw_data['Adj Close']
data.columns = tickers.keys()  # Renommer selon nos alias
data = data.dropna(how='all')  # Supprimer les lignes vides

# Calcul des performances
performance = (data.iloc[-1] / data.iloc[0] - 1) * 100
performance = performance.round(2)

# Application de la stratégie
if max(performance['AGG'], performance['TLT']) > max(performance['SXR8'], performance['ACWX']):
    result = 'AGG' if performance['AGG'] > performance['TLT'] else 'TLT'
else:
    if performance['SXR8'] > performance['ACWX']:
        result = 'SXR8' if performance['SXR8'] > performance['US03MY'] else 'US03MY'
    else:
        result = 'ACWX' if performance['ACWX'] > performance['US03MY'] else 'US03MY'

# Affichage dans Streamlit
st.title("📊 Stratégie Dual Momentum - Performance sur 12 Mois")

# Tableau de performance
df_perf = pd.DataFrame(performance).reset_index()
df_perf.columns = ['ETF', 'Performance 12M (%)']
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Résultat final en surbrillance jaune
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Résultat : {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
