import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Période de 12 mois glissants
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Tickers à suivre
tickers = {
    'AGG': 'AGG',
    'TLT': 'TLT',
    'SXR8': 'SXR8.DE',
    'ACWX': 'ACWX',
    'US03MY': '^IRX'
}

returns = {}

print(f"📅 Période analysée : {start_date.date()} → {end_date.date()}\n")

for name, ticker in tickers.items():
    print(f"📥 Téléchargement de {name} ({ticker})...")

    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if df.empty:
            print(f"⚠️  Données vides pour {name} ({ticker})")
            returns[name] = None
            continue

        print(f"✅ {name} : {len(df)} lignes chargées")

        # Afficher un aperçu
        print(df.head(2))

        prices = None
        if 'Adj Close' in df.columns:
            prices = df['Adj Close'].dropna()
        elif 'Close' in df.columns:
            prices = df['Close'].dropna()

        if prices is None or len(prices) < 2:
            print(f"⚠️  Données insuffisantes pour {name}")
            returns[name] = None
            continue

        perf = (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100
        returns[name] = perf

    except Exception as e:
        print(f"❌ Erreur lors du traitement de {name} : {e}")
        returns[name] = None

# Afficher tous les résultats
print("\n📊 Rendements sur 12 mois :")
for name, perf in returns.items():
    if isinstance(perf, (int, float)):
        print(f"{name}: {perf:.2f}%")
    else:
        print(f"{name}: Données indisponibles")

# Appliquer la logique finale si données complètes
required_keys = ['AGG', 'TLT', 'SXR8', 'ACWX', 'US03MY']
if not all(k in returns and isinstance(returns[k], (int, float)) for k in required_keys):
    print("\n🚫 Données incomplètes, impossible de sélectionner un actif.")
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

    print(f"\n✅ Actif sélectionné pour ce mois : {selected}")
