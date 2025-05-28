from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

etfs = {
    "AGG (US Bonds CT)": "AGG",
    "TLT (US Bonds LT)": "TLT",
    "SXR8 (US Equities)": "SXR8.DE",
    "ACWX (World ex US)": "ACWX",
    "US03MY (US Treasury)": "^IRX"  # Approximation taux sans risque
}

def get_12m_perf(ticker):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    data = yf.download(ticker, start=start_date, end=end_date, interval="1mo", progress=False)
    if data.empty or "Adj Close" not in data:
        return None
    start_price = data["Adj Close"].iloc[0]
    end_price = data["Adj Close"].iloc[-1]
    return (end_price - start_price) / start_price

performances = {name: get_12m_perf(ticker) for name, ticker in etfs.items()}
performances = {k: v for k, v in performances.items() if v is not None}

decision = "Données insuffisantes"

if all(k in performances for k in etfs.keys()):
    perf_bonds = max(performances["AGG (US Bonds CT)"], performances["TLT (US Bonds LT)"])
    perf_stocks = max(performances["SXR8 (US Equities)"], performances["ACWX (World ex US)"])

    if perf_bonds > perf_stocks:
        decision = "AGG" if performances["AGG (US Bonds CT)"] > performances["TLT (US Bonds LT)"] else "TLT"
    else:
        if performances["SXR8 (US Equities)"] > performances["ACWX (World ex US)"]:
            decision = "SXR8" if performances["SXR8 (US Equities)"] > performances["US03MY (US Treasury)"] else "US03MY (Cash)"
        else:
            decision = "ACWX" if performances["ACWX (World ex US)"] > performances["US03MY (US Treasury)"] else "US03MY (Cash)"

print("\nPerformance sur 12 mois :")
for name, perf in performances.items():
    print(f"{name} : {perf:.2%}")

print(f"\n➡️ Décision stratégique : {decision}")
