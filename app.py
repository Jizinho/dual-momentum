import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers ETF à analyser
tickers = {
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT'
}

# Ticker du T-Bill 13 semaines
t_bill_ticker = '^IRX'

# Définir la période d’analyse sur 12 mois
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Télécharger les données (sans auto_adjust)
raw_data = yf.download(
    list(tickers.values()),
    start=start_date,
    end=end_date,
    group_by='ticker',
    auto_adjust=False  # Pour utiliser Adj Close manuellement
)

# Initialiser un DataFrame pour les Adj Close
data = pd.DataFrame()

for name, ticker in tickers.items():
    try:
        if isinstance(raw_data.columns, pd.MultiIndex):
            data[name] = raw_data[ticker]['Adj Close']
        else:
            data[name] = raw_data['Adj Close']
    except Exception as e:
        st.warning(f"Erreur lors de l'import de {name} ({ticker}) : {e}")

# Supprimer les lignes incomplètes
data = data.dropna()

# Calcul des performances sur les dates alignées
first_values = data.iloc[0]
last_values = data.iloc[-1]
performance = ((last_values / first_values) - 1) * 100
performance = performance.round(2)

# Télécharger le rendement du T-Bill (13 semaines)
try:
    irx_data = yf.download(t_bill_ticker, period="5d", interval="1d", progress=False)
    irx_yield_raw = irx_data['Close'].dropna().iloc[-1]
    t_bill_yield = round(float(irx_yield_raw), 2)  # En pourcentage
except Exception as e:
    st.error(f"Erreur de récupération du T-Bill : {e}")
    t_bill_yield = None

# Extraire les performances
sxr8_perf = float(performance.get('SXR8', 0))
acwx_perf = float(performance.get('ACWX', 0))
agg_perf = float(performance.get('AGG', 0))
tlt_perf = float(performance.get('TLT', 0))
t_bill_yield = float(t_bill_yield or 0)

# Appliquer la stratégie Dual Momentum
if max(agg_perf, tlt_perf) > max(sxr8_perf, acwx_perf):
    result = 'AGG' if agg_perf > tlt_perf else 'TLT'
else:
    if sxr8_perf > acwx_perf:
        result = 'SXR8' if sxr8_perf > t_bill_yield else 'Cash / T-Bills'
    else:
        result = 'ACWX' if acwx_perf > t_bill_yield else 'Cash / T-Bills'

# Interface utilisateur Streamlit
st.title("📊 Stratégie Dual Momentum - Analyse sur 12 Mois")

# Tableau des performances
df_perf = pd.DataFrame({
    'ETF': ['SXR8', 'ACWX', 'AGG', 'TLT'],
    'Performance 12M (%)': [sxr8_perf, acwx_perf, agg_perf, tlt_perf]
})
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Affichage du rendement des T-Bills
if t_bill_yield:
    st.markdown(f"**Rendement T-Bill (13 semaines)** : `{t_bill_yield:.2f}%`")

# Résultat de la stratégie
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Résultat : {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
