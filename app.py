import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers utilisés
tickers = {
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT',
    'US03MY': '^IRX'
}

# Dates d’analyse
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Télécharger les données
raw_data = yf.download(list(tickers.values()), start=start_date, end=end_date, group_by='ticker', auto_adjust=True)

# Initialiser le DataFrame de résultats
data = pd.DataFrame()

# Extraire les colonnes 'Close' ou 'Adj Close' manuellement
for name, ticker in tickers.items():
    try:
        if isinstance(raw_data.columns, pd.MultiIndex):
            # Format multi-index : (ticker, OHLC)
            series = raw_data[ticker]['Close']
        else:
            # Cas exceptionnel (1 seul ticker ou fallback)
            series = raw_data['Close']
        data[name] = series
    except Exception as e:
        st.warning(f"Erreur pour {name} ({ticker}) : {e}")

# Supprimer les lignes vides
data = data.dropna(how='all')

# Calculer les performances
performance = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
performance = performance.round(2)

# Appliquer la stratégie Dual Momentum
if max(performance['AGG'], performance['TLT']) > max(performance['SXR8'], performance['ACWX']):
    result = 'AGG' if performance['AGG'] > performance['TLT'] else 'TLT'
else:
    if performance['SXR8'] > performance['ACWX']:
        result = 'SXR8' if performance['SXR8'] > performance['US03MY'] else 'US03MY'
    else:
        result = 'ACWX' if performance['ACWX'] > performance['US03MY'] else 'US03MY'

# Interface Streamlit
st.title("📊 Stratégie Dual Momentum - Performance sur 12 Mois")

# Tableau des performances
df_perf = pd.DataFrame(performance).reset_index()
df_perf.columns = ['ETF', 'Performance 12M (%)']
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Résultat final mis en valeur
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Résultat : {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
