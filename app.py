import yfinance as yf
import pandas as pd
from datetime import datetime

# Liste des tickers Yahoo Finance
tickers = {
    'SXR8': 'SXR8.DE',     # ETF US
    'ACWX': 'ACWX',        # ETF Monde hors US
    'AGG': 'AGG',          # Obligations CT
    'TLT': 'TLT',          # Obligations LT
    'US03MY': '^IRX'       # Rendement 3 mois (remplacé par un proxy car 'US03MY.L' est incorrect)
}

# Dates
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(years=1)

# Téléchargement des données
data = yf.download(list(tickers.values()), start=start_date, end=end_date)['Adj Close']

# Nettoyage et renommage
data.columns = tickers.keys()  # Renomme les colonnes avec les clés (noms simples)
data = data.dropna(how='all')  # Supprime les lignes vides

# Calcul de performance 12 mois
performance = (data.iloc[-1] / data.iloc[0] - 1) * 100
performance = performance.round(2)

# Affichage des performances
print("Performance 12M (%) :\n")
print(performance)

# Application de la stratégie Dual Momentum
resultat = ""
if max(performance['AGG'], performance['TLT']) > max(performance['SXR8'], performance['ACWX']):
    resultat = 'AGG' if performance['AGG'] > performance['TLT'] else 'TLT'
else:
    if performance['SXR8'] > performance['ACWX']:
        resultat = 'SXR8' if performance['SXR8'] > performance['US03MY'] else 'US03MY'
    else:
        resultat = 'ACWX' if performance['ACWX'] > performance['US03MY'] else 'US03MY'

print("\nRésultat :", resultat)
