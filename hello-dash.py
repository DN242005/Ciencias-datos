import streamlit as st
import pandas as pd 
st.title("Jonathan")
st.title("hello world web")
st.write("hello world streamlit")
dataframe = pd.read_csv("https://raw.githubusercontent.com/adsoftsito/ciencia-datos/refs/heads/main/titanic.csv")
st.dataframe(dataframe)
st.write("by adsoftsito")
