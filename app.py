import yfinance as yf
import pandas as pd
from datetime import datetime

# Liste des tickers à analyser
tickers = ['SXR8.L', 'ACWX.L', 'AGG.L', 'TLT.L', 'US03MY.L']

# Récupération des données historiques
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)
data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

# Calcul de la performance 12 mois
performance = (data.iloc[-1] / data.iloc0] - 1) * 100

# Application de la stratégie Dual Momentum
def apply_dual_momentum(perf):
    # Comparaison obligations vs actions
    bond_perf = max(perf['AGG.L'], perf['TLT.L'])
    stock_perf = max(perf['SXR8.L'], perf['ACWX.L'])
    
    result = "Résultat final : "
    
    if bond_perf > stock_perf:
        result += "AGG" if perf['AGG.L'] > perf['TLT.L'] else "TLT"
    else:
        if perf['SXR8.L'] > perf['ACWX.L']:
            result += "SXR8" if perf['SXR8.L'] > perf['US03MY.L'] else "US03MY"
        else:
            result += "ACWX" if perf['ACWX.L'] > perf['US03MY.L'] else "US03MY"
    
    return result

# Affichage des résultats
print("Performance des actifs sur 12 mois :")
for ticker, perf in performance.items():
    print(f"{ticker}: {perf:.2f}%")

print("\n" + apply_dual_momentum(performance))
