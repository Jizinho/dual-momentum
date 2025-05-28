import yfinance as yf
import pandas as pd
import streamlit as st

tickers = {
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'AGG': 'AGG',
    'TLT': 'TLT'
}

t_bill_ticker = '^IRX'

# Dates d’analyse
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

def get_total_return(ticker):
    # Télécharge les prix
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
    
    # Récupère les dividendes
    dividends = yf.Ticker(ticker).dividends
    dividends.index = pd.to_datetime(dividends.index)  # ✅ conversion nécessaire ici
    
    # Filtrer la période
    dividends = dividends[(dividends.index >= start_date) & (dividends.index <= end_date)]
    
    # Prix d'entrée et de sortie
    price_start = data['Close'].iloc[0]
    price_end = data['Close'].iloc[-1]
    
    # Rendement total avec dividendes
    total_dividends = dividends.sum() if not dividends.empty else 0
    total_return = ((price_end + total_dividends) / price_start - 1) * 100
    return round(total_return, 2)

# Récupérer performances de tous les actifs
perf = {name: get_total_return(ticker) for name, ticker in tickers.items()}

# Récupérer taux du T-Bill
try:
    irx_data = yf.download(t_bill_ticker, period="5d", interval="1d", progress=False)
    irx_yield_raw = irx_data['Close'].dropna().iloc[-1]
    t_bill_yield = round(float(irx_yield_raw), 2)
except Exception as e:
    st.error(f"Erreur T-Bill : {e}")
    t_bill_yield = 0

# Appliquer la stratégie Dual Momentum
if max(perf['AGG'], perf['TLT']) > max(perf['SXR8'], perf['ACWX']):
    result = 'AGG' if perf['AGG'] > perf['TLT'] else 'TLT'
else:
    if perf['SXR8'] > perf['ACWX']:
        result = 'SXR8' if perf['SXR8'] > t_bill_yield else 'Cash / T-Bills'
    else:
        result = 'ACWX' if perf['ACWX'] > t_bill_yield else 'Cash / T-Bills'

# Interface Streamlit
st.title("📊 Stratégie Dual Momentum - Rendement Total (12 Mois)")

df_perf = pd.DataFrame(list(perf.items()), columns=['ETF', 'Performance 12M (%)'])
st.dataframe(df_perf.style.format({'Performance 12M (%)': '{:.2f}'}), use_container_width=True)

st.markdown(f"**Rendement T-Bill (13 semaines)** : `{t_bill_yield:.2f}%`")

st.markdown(
    f"<div style='background-color: yellow; padding: 10px; font-size: 20px; text-align: center;'>"
    f"<strong>Résultat : {result}</strong>"
    f"</div>",
    unsafe_allow_html=True
)
