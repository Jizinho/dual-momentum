from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

# Liste des ETFs et taux
etfs = {
    "AGG (US Bonds CT)": "AGG",
    "TLT (US Bonds LT)": "TLT",
    "VOO (US Equities)": "VOO",
    "ACWX (World ex US)": "ACWX",
    "US03MY (US Treasury)": "^IRX",  # proxy pour taux court terme US
}

# Fonction pour calculer la performance sur 12 mois
def get_12m_perf(ticker):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    data = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    if data.empty or "Adj Close" not in data.columns:
        print(f"Aucune donnée pour {ticker}")
        return None
    data = data["Adj Close"].dropna()
    if len(data) < 2:
        return None
    return (data.iloc[-1] - data.iloc[0]) / data.iloc[0]

# Récupération des performances
performances = {name: get_12m_perf(ticker) for name, ticker in etfs.items()}
performances_cleaned = {k: v for k, v in performances.items() if v is not None}

print("Performance sur 12 mois :")
for k, v in performances_cleaned.items():
    print(f"{k} : {v:.2%}")

# Logique de décision
decision = "➡️ Décision stratégique : Données insuffisantes"
if all(k in performances_cleaned for k in ["AGG (US Bonds CT)", "TLT (US Bonds LT)", "VOO (US Equities)", "ACWX (World ex US)", "US03MY (US Treasury)"]):
    bonds = max(performances_cleaned["AGG (US Bonds CT)"], performances_cleaned["TLT (US Bonds LT)"])
    equities = max(performances_cleaned["VOO (US Equities)"], performances_cleaned["ACWX (World ex US)"])
    if bonds > equities:
        decision = "➡️ Obligation en tête : AGG" if performances_cleaned["AGG (US Bonds CT)"] > performances_cleaned["TLT (US Bonds LT)"] else "➡️ Obligation en tête : TLT"
    else:
        if performances_cleaned["VOO (US Equities)"] > performances_cleaned["ACWX (World ex US)"]:
            if performances_cleaned["VOO (US Equities)"] > performances_cleaned["US03MY (US Treasury)"]:
                decision = "➡️ Action US sélectionnée (VOO)"
        else:
            if performances_cleaned["ACWX (World ex US)"] > performances_cleaned["US03MY (US Treasury)"]:
                decision = "➡️ Action Monde ex-US sélectionnée (ACWX)"

print()
print(decision)
