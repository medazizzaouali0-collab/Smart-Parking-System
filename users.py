import streamlit as st
import sqlite3
import pandas as pd

# Connexion à votre base de données
conn = sqlite3.connect('users.db')

# Requête pour récupérer les utilisateurs
query = "SELECT * FROM users" # Remplacez 'users' par le nom de votre table
df = pd.read_sql_query(query, conn)

# Affichage dans Streamlit
st.subheader("Liste des utilisateurs")
st.dataframe(df)

conn.close()
