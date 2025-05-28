import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Titre de l'application
st.title("Dual Momentum - Décision mensuelle")
st.markdown("Calcule la performance des actifs sur les 12 derniers mois et prend une décision.")

# Génération de données simulées (tu pourras les remplacer par des données réelles)
@st.cache_data
def generate_data():
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", end="2025-01-15", freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'AGG': np.cumprod(1 + np.random.normal(0, 0.0005, len(dates))),
        'TLT': np.cumprod(1 + np.random.normal(0, 0.001, len(dates))),
        'SXR8': np.cumprod(1 + np.random.normal(0.0005, 0.002, len(dates))),
        'ACWX': np.cumprod(1 + np.random.normal(0.0006, 0.0025, len(dates))),
        'US03MY': np.cumprod(1 + np.random.normal(0.0001, 0.0002, len(dates)))
    }).set_index('Date')
    return data

# Calcul de la performance sur 12 mois
def performance_12m(df, date):
    one_year_ago = date - pd.DateOffset(years=1)
    if one_year_ago < df.index[0]:
        return None
    return (df.loc[date] / df.loc[one_year_ago]) - 1

# Logique de décision
def dual_momentum_decision(data, date):
    perf = performance_12m(data, date)
    if perf is None:
        return "Pas assez de données pour une décision."

    # Formattage des performances
    perf_str = {
        "SXR8": f"{perf['SXR8'] * 100:.2f} %",
        "ACWX": f"{perf['ACWX'] * 100:.2f} %",
        "AGG": f"{perf['AGG'] * 100:.2f} %",
        "TLT": f"{perf['TLT'] * 100:.2f} %",
        "US03MY": f"{perf['US03MY'] * 100:.2f} %"
    }

    # Comparaison obligations vs actions
    bond_perf = max(perf['AGG'], perf['TLT'])
    stock_perf = max(perf['SXR8'], perf['ACWX'])

    result = (
        f"SXR8 : {perf_str['SXR8']}\n"
        f"ACWX : {perf_str['ACWX']}\n"
        f"AGG : {perf_str['AGG']}\n"
        f"TLT : {perf_str['TLT']}\n"
        f"US03MY : {perf_str['US03MY']}\n"
    )

    if bond_perf > stock_perf:
        if perf['AGG'] > perf['TLT']:
            result += "Résultat : AGG"
        else:
            result += "Résultat : TLT"
    else:
        if perf['SXR8'] > perf['ACWX']:
            if perf['SXR8'] > perf['US03MY']:
                result += "Résultat : SXR8"
            else:
                result += "Résultat : US03MY"
        else:
            if perf['ACWX'] > perf['US03MY']:
                result += "Résultat : ACWX"
            else:
                result += "Résultat : US03MY"

    return result

# Génération des données
data = generate_data()

# Interface utilisateur
st.subheader("Choisir une date pour la décision")
selected_date = st.date_input("Sélectionnez une date", value=datetime(2025, 1, 1))

# Conversion en datetime compatible avec l'index
selected_date = pd.to_datetime(selected_date)

# Vérifier si c'est le 1er du mois
if selected_date.day != 1:
    st.warning("⚠️ La stratégie doit être exécutée uniquement le 1er du mois.")
else:
    if st.button("Calculer la performance et prendre une décision"):
        decision = dual_momentum_decision(data, selected_date)
        st.text(décision)
