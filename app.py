import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('ejecucion_agosto.csv')
st.title("Ejecución")

st.dataframe(df) 

# ejecucion (obligación)
# perdida de apropiación (compromiso)
