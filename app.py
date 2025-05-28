import streamlit as st
import pandas as pd
from datetime import datetime

# Titre de l'application
st.title("Dual Momentum Strategy - Analyse et Décision")

# Section d'upload du fichier
uploaded_file = st.file_uploader("Téléchargez votre fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Charger les données
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file parse_dates=['Date'], index_col='Date')
        else:  # Fichier Excel
            data = pd.read_excel(uploaded_file, parse_dates=['Date'], index_col='Date')
        
        st.success("✅ Fichier chargé avec succès !")
        
        # Afficher un aperçu des données
        st.subheader("Aperçu des données")
        st.dataframe(data.tail())
        
        # Fonction pour calculer la performance sur 12 mois
        def performance_12m(df, date):
            one_year_ago = date - pd.DateOffset(years=1)
            if one_year_ago < df.index[0]:
                return None
            return (df.loc[date] / df.loc[one_year_ago]) - 1
        
        # Logique de décision Dual Momentum
        def dual_momentum_decision(data, date):
            perf = performance_12m(data, date)
            if perf is None:
                return "Pas assez de données pour une décision."
            
            # Formattage des performances
            perf_str = {key: f"{value * 100:.2f} %" for key, value in perf.items()}
            
            result = "\n".join([f"{key} : {value}" for key, value in perf_str.items()])
            
            # Comparaison obligations vs actions
            bond_perf = max(perf['AGG'], perf['TLT'])
            stock_perf = max(perf['SXR8'], perf['ACWX'])
            
            if bond_perf > stock_perf:
                result += "\nRésultat : AGG" if perf['AGG'] > perf['TLT'] else "\nRésultat : TLT"
            else:
                if perf['SXR8'] > perf['ACWX']:
                    if perf['SXR8'] > perf['US03MY']:
                        result += "\nRésultat : SXR8"
                    else:
                        result += "\nRésultat : US03MY"
                else:
                    if perf['ACWX'] > perf['US03MY']:
                        result += "\nRésultat : ACWX"
                    else:
                        result += "\nRésultat : US03MY"
            
            return result
        
        # Interface utilisateur pour la date
        st.subheader("📅 Choisir une date pour la décision")
        selected_date = st.date_input("Sélectionnez une date", value=datetime(2025, 1, 1))
        selected_date = pd.to_datetime(selected_date)
        
        if selected_date.day != 1:
            st.warning("⚠️ La stratégie doit être exécutée uniquement le 1er du mois.")
        else:
            if st.button("Calculer la performance et prendre une décision"):
                decision = dual_momentum_decision(data, selected_date)
                st.text(decision)
    
    except Exception as e:
        st.error(f"Une erreur s'est produite : {str(e)}")
        st.info("Vérifiez que votre fichier contient bien les colonnes nécessaires (SXR8, ACWX, AGG, TLT, US03MY) et que le format de la date est correct.")

else:
    st.info("📂 Veuillez télécharger un fichier pour commencer.")
