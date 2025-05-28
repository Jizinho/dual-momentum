import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Définir la période
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Tickers à surveiller
tickers = {
    'AGG': 'AGG',
    'TLT': 'TLT',
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'US03MY': '^IRX'
}

# Télécharger et stocker les données
returns = {}
for name, ticker in tickers.items():
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        print(f"[⚠️] Données indisponibles pour {name} ({ticker})")
        continue

    # Essayer d’utiliser 'Adj Close', sinon 'Close'
    try:
        prices = df['Adj Close']
    except KeyError:
        try:
            prices = df['Close']
        except KeyError:
            print(f"[❌] Ni 'Adj Close' ni 'Close' trouvés pour {name}")
            continue

    if len(prices) >= 2:
        returns[name] = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
    else:
        print(f"[ℹ️] Pas assez de données pour {name}")

# Afficher les rendements
print("\n📊 Rendements sur 12 mois :")
for name, perf in returns.items():
    print(f"{name}: {perf:.2f}%")

# Logique de sélection
required_keys = ['AGG', 'TLT', 'SXR8', 'ACWX', 'US03MY']
if not all(k in returns for k in required_keys):
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

    print(f"\n✅ Actif sélectionné : {selected}")
