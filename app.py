import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Période de 12 mois
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Liste des tickers
tickers = {
    'AGG': 'AGG',
    'TLT': 'TLT',
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'US03MY': '^IRX'
}

returns = {}

for name, ticker in tickers.items():
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if df.empty:
            print(f"[⚠️] Données absentes pour {name} ({ticker})")
            returns[name] = None
            continue

        # Sélection de la colonne de prix
        prices = None
        if 'Adj Close' in df.columns:
            prices = df['Adj Close'].dropna()
        elif 'Close' in df.columns:
            prices = df['Close'].dropna()

        if prices is None or len(prices) < 2:
            print(f"[⚠️] Données insuffisantes pour {name}")
            returns[name] = None
            continue

        # Calcul de performance
        perf = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
        returns[name] = perf

    except Exception as e:
        print(f"[❌] Erreur lors du traitement de {name}: {e}")
        returns[name] = None

# Affichage des performances
print("\n📊 Rendements sur 12 mois :")
for name, perf in returns.items():
    if isinstance(perf, (int, float)):
        print(f"{name}: {perf:.2f}%")
    else:
        print(f"{name}: Données indisponibles")

# Application de la logique de stratégie
required_keys = ['AGG', 'TLT', 'SXR8', 'ACWX', 'US03MY']
if not all(k in returns and isinstance(returns[k], (int, float)) for k in required_keys):
    print("\n[🚫] Données incomplètes pour appliquer la stratégie.")
else:
    avg_bonds = (returns['AGG'] + returns['TLT']) / 2
    avg_stocks = (returns['SXR8'] + returns['ACWX']) / 2

    if avg_bonds > avg_stocks:
        selected = 'AGG' if returns['AGG'] > returns['TLT'] else 'TLT'
    else:
        if returns['SXR8'] > returns['ACWX']:
            selected = 'SXR8' if returns['SXR8'] > returns['US03MY'] else 'US03MY'
        else:
            selected = 'ACWX' if returns['ACWX'] > returns['US03MY'] else 'US03MY'

    print(f"\n✅ Actif sélectionné pour le mois : {selected}")
