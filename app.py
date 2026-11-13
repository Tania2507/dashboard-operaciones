import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Operaciones",
    layout="wide"
)

st.title("📊 Dashboard Operaciones")

archivo = st.file_uploader(
    "Cargar archivo Excel",
    type=["xlsx"]
)

if archivo:

    df = pd.read_excel(archivo)

    st.success("Archivo cargado correctamente")

    st.write("Vista previa")

    st.dataframe(df.head())

    st.metric(
        "Total Casos",
        len(df)
    )
