import yfinance as yf
import pandas as pd
import streamlit as st

# Mapping tickers to readable asset names
tickers = {
    'US S&P500': 'SXR8.DE',
    'World ex.US': 'ACWX',
    'CT Bonds': 'AGG',
    'LT Bonds': 'TLT',
    'Treasury Bonds': '^IRX'
}

# Dates d’analyse
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Téléchargement des données
raw_data = yf.download(list(tickers.values()), start=start_date, end=end_date, group_by='ticker', auto_adjust=True)

# Initialiser le DataFrame
data = pd.DataFrame()

# Extraire les données par ticker
for name, ticker in tickers.items():
    try:
        if isinstance(raw_data.columns, pd.MultiIndex):
            series = raw_data[ticker]['Close']
        else:
            series = raw_data['Close']
        data[name] = series
    except Exception as e:
        st.warning(f"Erreur pour {name} ({ticker}) : {e}")

# Nettoyer les données
data = data.dropna(how='all')

# Calcul des performances sur 12 mois
performance = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
performance = performance.round(2)

# Appliquer la stratégie Dual Momentum
if max(performance['CT Bonds'], performance['LT Bonds']) > max(performance['US S&P500'], performance['World ex.US']):
    result = 'CT Bonds' if performance['CT Bonds'] > performance['LT Bonds'] else 'LT Bonds'
else:
    if performance['US S&P500'] > performance['World ex.US']:
        result = 'US S&P500' if performance['US S&P500'] > performance['Treasury Bonds'] else 'Treasury Bonds'
    else:
        result = 'World ex.US' if performance['World ex.US'] > performance['Treasury Bonds'] else 'Treasury Bonds'

# Affichage dans Streamlit
st.markdown("# Dual Momentum Investing")
st.markdown("*1 year performance*")

# Tableau de performances
df_perf = pd.DataFrame(performance).reset_index()
df_perf.columns = ['Asset', 'Performance 12M (%)']
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Affichage du résultat final
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Selected Asset: {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
