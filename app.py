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

# Télécharger les données
data = pd.DataFrame()
for name, ticker in tickers.items():
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
        data[name] = df['Close']
    except Exception as e:
        st.warning(f"Erreur pour {name} ({ticker}) : {e}")

# Nettoyer les données
data = data.dropna(how='any')

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

# Interface Streamlit
st.markdown("# Dual Momentum Investing")
st.markdown("*1 year performance*")

# Tableau de performances
df_perf = pd.DataFrame(performance).reset_index()
df_perf.columns = ['Asset', 'Performance 12M (%)']
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Résultat final mis en valeur
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Selected Asset: {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
