import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Panel de control de operaciones",
    layout="wide"
)

st.title("📊 Panel de control de operaciones")

archivo = st.file_uploader(
    "Cargar archivo Excel",
    type=["xlsx"]
)

if archivo:

    df = pd.read_excel(archivo)

    st.success("Archivo cargado correctamente")

    st.subheader("Vista previa")

    st.dataframe(df.head())

    st.metric(
        "Total Casos",
        len(df)
    )
