import streamlit as st
import pandas as pd

st.title("Dashboard de Autos - Ciencia de Datos")
st.write("Visualización de datos del dataset Cars93")


url = "https://raw.githubusercontent.com/DN242005/Ciencias-datos/main/Cars93.csv"
dataframe = pd.read_csv(url)


st.dataframe(dataframe)

st.bar_chart(dataframe["Price"])