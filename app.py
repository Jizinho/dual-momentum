import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers ETF à analyser (hors IRX)
tickers = {
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT'
}

# Ticker du rendement sans risque (13-week T-Bill)
t_bill_ticker = '^IRX'

# Période d’analyse : 12 mois
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Télécharger les données des ETF
raw_data = yf.download(list(tickers.values()), start=start_date, end=end_date, group_by='ticker', auto_adjust=True)

# Extraire les prix de clôture dans un DataFrame propre
data = pd.DataFrame()

for name, ticker in tickers.items():
    try:
        if isinstance(raw_data.columns, pd.MultiIndex):
            data[name] = raw_data[ticker]['Close']
        else:
            data[name] = raw_data['Close']
    except Exception as e:
        st.warning(f"Erreur lors de l'import de {name} ({ticker}) : {e}")

# Nettoyer les données
data = data.dropna(how='all')

# Calcul de la performance 12 mois (%)
performance = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
performance = performance.round(2)

# Télécharger la dernière valeur de IRX (rendement T-Bill 13 semaines)
try:
    irx_data = yf.download(t_bill_ticker, period="5d", interval="1d", progress=False)
    irx_yield_raw = irx_data['Close'].dropna().iloc[-1]
    t_bill_yield = round(irx_yield_raw, 2)  # déjà en %, pas besoin de diviser par 100
except Exception as e:
    st.error(f"Erreur de téléchargement de IRX : {e}")
    t_bill_yield = None

# Appliquer la stratégie Dual Momentum
if t_bill_yield is not None:
    if max(performance['AGG'], performance['TLT']) > max(performance['SXR8'], performance['ACWX']):
        result = 'AGG' if performance['AGG'] > performance['TLT'] else 'TLT'
    else:
        if performance['SXR8'] > performance['ACWX']:
            result = 'SXR8' if performance['SXR8'] > t_bill_yield else 'Cash / T-Bills'
        else:
            result = 'ACWX' if performance['ACWX'] > t_bill_yield else 'Cash / T-Bills'
else:
    result = 'Erreur : taux T-Bill indisponible'

# Interface Streamlit
st.title("📊 Stratégie Dual Momentum - Performance sur 12 Mois")

# Tableau des performances
df_perf = pd.DataFrame(performance).reset_index()
df_perf.columns = ['ETF', 'Performance 12M (%)']
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Affichage du taux sans risque
if t_bill_yield is not None:
    st.markdown(f"**Rendement T-Bill (13 semaines)** : `{t_bill_yield:.2f}%`")

# Résultat
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Résultat : {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
