import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Définir la date de début (12 mois en arrière)
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Télécharger les données des ETFs
tickers = {
    'AGG': 'AGG',
    'TLT': 'TLT',
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'US03MY': '^IRX'  # Taux des bons du Trésor US à 3 mois
}

data = {}
for name, ticker in tickers.items():
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        print(f"Les données pour {name} ({ticker}) sont indisponibles.")
        continue
    data[name] = df['Adj Close']

# Calculer les rendements sur 12 mois
returns = {}
for name, prices in data.items():
    if len(prices) < 2:
        continue
    returns[name] = (prices[-1] - prices[0]) / prices[0] * 100

# Afficher les rendements
print("Rendements sur 12 mois :")
for name, ret in returns.items():
    print(f"{name}: {ret:.2f}%")

# Logique de sélection
selected_asset = None

# Vérifier si les données nécessaires sont disponibles
required_keys = ['AGG', 'TLT', 'SXR8', 'ACWX', 'US03MY']
if not all(key in returns for key in required_keys):
    print("Données insuffisantes pour effectuer la sélection.")
else:
    avg_bonds = (returns['AGG'] + returns['TLT']) / 2
    avg_stocks = (returns['SXR8'] + returns['ACWX']) / 2

    if avg_bonds > avg_stocks:
        # Les obligations performent mieux
        selected_asset = 'AGG' if returns['AGG'] > returns['TLT'] else 'TLT'
    else:
        # Les actions performent mieux
        if returns['SXR8'] > returns['ACWX']:
            selected_asset = 'SXR8' if returns['SXR8'] > returns['US03MY'] else 'US03MY'
        else:
            selected_asset = 'ACWX' if returns['ACWX'] > returns['US03MY'] else 'US03MY'

    print(f"\nActif sélectionné pour le mois : {selected_asset}")
