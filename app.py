import yfinance as yf
import pandas as pd
import streamlit as st

# Tickers ETF à suivre
tickers = {
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT'
}

# Ticker du T-Bill 13 semaines (taux sans risque)
t_bill_ticker = '^IRX'

# Définir la période d’analyse : 12 mois
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Télécharger les données des ETF
raw_data = yf.download(list(tickers.values()), start=start_date, end=end_date, group_by='ticker', auto_adjust=True)

# Initialiser un DataFrame pour les prix de clôture
data = pd.DataFrame()

for name, ticker in tickers.items():
    try:
        if isinstance(raw_data.columns, pd.MultiIndex):
            data[name] = raw_data[ticker]['Close']
        else:
            data[name] = raw_data['Close']
    except Exception as e:
        st.warning(f"Erreur lors de l'import de {name} ({ticker}) : {e}")

# Nettoyage des données
data = data.dropna(how='all')

# Calcul de la performance 12 mois (%)
try:
    performance = ((data.iloc[-1] / data.iloc[0]) - 1) * 100
    performance = performance.round(2)
    performance = pd.Series(performance)  # Forcer un Series bien formé
except Exception as e:
    st.error(f"Erreur lors du calcul des performances : {e}")
    performance = pd.Series()

# Télécharger la dernière valeur de ^IRX (rendement sans risque)
try:
    irx_data = yf.download(t_bill_ticker, period="5d", interval="1d", progress=False)
    irx_yield_raw = irx_data['Close'].dropna().iloc[-1]
    t_bill_yield = round(float(irx_yield_raw), 2)  # Exprimé en pourcentage
except Exception as e:
    st.error(f"Erreur de récupération du T-Bill : {e}")
    t_bill_yield = None

# Forcer les performances en float pour éviter toute ambiguïté
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

# Interface Streamlit
st.title("📊 Stratégie Dual Momentum - Analyse 12 Mois")

# Affichage des performances
df_perf = pd.DataFrame({
    'ETF': ['SXR8', 'ACWX', 'AGG', 'TLT'],
    'Performance 12M (%)': [sxr8_perf, acwx_perf, agg_perf, tlt_perf]
})
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

# Affichage du T-Bill
if t_bill_yield:
    st.markdown(f"**Rendement T-Bill (13 semaines)** : `{t_bill_yield:.2f}%`")

# Résultat
st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Résultat : {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
