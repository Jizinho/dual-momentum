import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers utilisés
tickers = {
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT'
}

# Ticker T-Bill (rendement sans risque)
t_bill_ticker = '^IRX'

# Dates d’analyse
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Télécharger les données des ETF
raw_data = yf.download(list(tickers.values()), start=start_date, end=end_date, group_by='ticker', auto_adjust=True)

# Initialiser le DataFrame de prix
data = pd.DataFrame()

# Extraire les prix de clôture
for name, ticker in tickers.items():
    try:
        if isinstance(raw_data.columns, pd.MultiIndex):
            series = raw_data[ticker]['Close']
        else:
            series = raw_data['Close']
        data[name] = series
    except Exception as e:
        st.warning(f"Erreur pour {name} ({ticker}) : {e}")

# Supprimer les lignes vides
data = data.dropna(how='all')

# Calcul de la performance 12 mois (%)
performance = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
performance = performance.round(2)

# Télécharger la dernière valeur du T-Bill
try:
    t_bill_data = yf.download(t_bill_ticker, period="5d", interval="1d", progress=False)
    t_bill_yield = t_bill_data['Close'].dropna().iloc[-1]
except Exception as e:
    t_bill_yield = None
    st.error(f"Impossible de récupérer le rendement des T-Bills ({t_bill_ticker}) : {e}")

# Appliquer la stratégie Dual Momentum
if t_bill_yield is not None:
    # Comparaison avec rendement réel, pas en % de perf
    if max(performance['AGG'], performance['TLT']) > max(performance['SXR8'], performance['ACWX']):
        result = 'AGG' if performance['AGG'] > performance['TLT'] else 'TLT'
    else:
        if performance['SXR8'] > performance['ACWX']:
            result = 'SXR8' if performance['SXR8'] > t_bill_yield else 'Liquidité / Cash (T-Bills)'
        else:
            result = 'ACWX' if performance['ACWX'] > t_bill_yield else 'Liquidité / Cash (T-Bills)'
else:
    result = 'Erreur : rendement T-Bills indisponible'

# Interface Streamlit
st.title("📊 Stratégie Dual Momentum - Performance sur 12 Mois")

# Affichage des performances
df_perf = pd.DataFrame(performance).reset_index()
df_perf.columns = ['ETF', 'Performance 12M (%)']
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Affichage du taux T-Bill
if t_bill_yield is not None:
    st.markdown(f"**Rendement T-Bill actuel (13 semaines)** : `{t_bill_yield:.2f}%`")

# Résultat final
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Résultat : {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
