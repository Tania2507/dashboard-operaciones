import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os

# ==================================
# CONFIGURACION
# ==================================

st.set_page_config(
    page_title="Panel de Control Operaciones",
    layout="wide"
)

ARCHIVO_GUARDADO = "ultimo_archivo.xlsx"
PASSWORD = "Operaciones2026"

st.title("📊 Panel de Control Operaciones")

# ==================================
# ACTUALIZAR ARCHIVO
# ==================================

with st.expander("🔒 Actualizar información"):

    password = st.text_input(
        "Ingrese contraseña para cargar un nuevo archivo",
        type="password"
    )

    if password == PASSWORD:

        nuevo_archivo = st.file_uploader(
            "Seleccione el archivo Excel",
            type=["xlsx"]
        )

        if nuevo_archivo:

            with open(
                ARCHIVO_GUARDADO,
                "wb"
            ) as f:

                f.write(
                    nuevo_archivo.getbuffer()
                )

            st.success(
                "✅ Archivo actualizado correctamente"
            )

    elif password != "":
        st.error(
            "❌ Contraseña incorrecta"
        )

# ==================================
# VALIDAR EXISTENCIA
# ==================================

if not os.path.exists(
    ARCHIVO_GUARDADO
):
    st.warning(
        "Aún no se ha cargado ningún archivo."
    )
    st.stop()

# ==================================
# LEER ARCHIVO GUARDADO
# ==================================

df = pd.read_excel(
    ARCHIVO_GUARDADO
)

# ==================================
# OPERACIONES
# ==================================

operaciones = [
    "DC Validacion SARLAFT",
    "DC Renovacion",
    "DC Configuracion",
    "DC Expedicion",
    "DC Imagine"
]

# ==================================
# OTRAS AREAS
# ==================================

otras_areas = [
    "DC Facturacion Vencida",
    "DC Vigencia Futura",
    "DC Pendiente Blanket",
    "DC Area Tecnica",
    "DC Novedades",
    "DC Actualizacion FCC y Anexos",
    "DC Analisis Segurabilidad",
    "DC Analisis Tecnico",
    "DC Validacion Inicial",
    "DC Exequiel Familiar"
]

# ==================================
# VALIDACION COLUMNAS
# ==================================

for col in operaciones + otras_areas:

    if col not in df.columns:
        df[col] = 0

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# ==================================
# CALCULOS
# ==================================

df["Dias Operaciones"] = (
    df[operaciones]
    .sum(axis=1)
    .round(2)
)

df["Dias Otras Areas"] = (
    df[otras_areas]
    .sum(axis=1)
    .round(2)
)

# ==================================
# CLASIFICACION
# ==================================

def clasificar(dias):

    if dias <= 4:
        return "🟢 1 a 4 días"

    elif dias <= 6:
        return "🟡 5 a 6 días"

    else:
        return "🔴 Más de 6 días"

df["Clasificacion"] = (
    df["Dias Operaciones"]
    .apply(clasificar)
)

# ==================================
# INDICADORES
# ==================================

total_casos = len(df)

casos_1_4 = len(
    df[df["Clasificacion"] == "🟢 1 a 4 días"]
)

casos_5_6 = len(
    df[df["Clasificacion"] == "🟡 5 a 6 días"]
)

casos_mas_6 = len(
    df[df["Clasificacion"] == "🔴 Más de 6 días"]
)

cumplimiento = round(
    (casos_1_4 / total_casos) * 100,
    2
) if total_casos > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Total Casos",
    total_casos
)

c2.metric(
    "🟢 Casos 1-4 días",
    casos_1_4
)

c3.metric(
    "🟡 Casos 5-6 días",
    casos_5_6
)

c4.metric(
    "🔴 Casos > 6 días",
    casos_mas_6
)

c5.metric(
    "% Cumplimiento",
    f"{cumplimiento}%"
)

st.divider()

# ==================================
# GRAFICO DONA
# ==================================

resumen = pd.DataFrame({
    "Clasificacion": [
        "🟢 1 a 4 días",
        "🟡 5 a 6 días",
        "🔴 Más de 6 días"
    ],
    "Cantidad": [
        casos_1_4,
        casos_5_6,
        casos_mas_6
    ]
})

fig = px.pie(
    resumen,
    names="Clasificacion",
    values="Cantidad",
    hole=0.55,
    title="Distribución de Casos"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================
# TOP 10 OPERACIONES
# ==================================

st.subheader(
    "🚨 Top 10 Casos con Mayor Tiempo en Operaciones"
)

top10 = df.sort_values(
    by="Dias Operaciones",
    ascending=False
).head(10)

columnas_top10 = [
    c for c in [
        "Radicado",
        "Razon Social",
        "Dias Operaciones",
        "Dias Otras Areas"
    ]
    if c in top10.columns
]

st.dataframe(
    top10[columnas_top10],
    use_container_width=True
)

# ==================================
# GRAFICO TOP 10
# ==================================

if "Radicado" in top10.columns:

    fig2 = px.bar(
        top10,
        x="Radicado",
        y="Dias Operaciones",
        text="Dias Operaciones",
        title="Top 10 Casos con Mayor Tiempo"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ==================================
# CASOS CRITICOS
# ==================================

st.subheader(
    "🔴 Casos con Más de 6 Días"
)

criticos = df[
    df["Dias Operaciones"] > 6
]

st.dataframe(
    criticos,
    use_container_width=True
)

# ==================================
# DESCARGA
# ==================================

salida = BytesIO()

with pd.ExcelWriter(
    salida,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        index=False,
        sheet_name="Resultados"
    )

st.download_button(
    "📥 Descargar Excel Procesado",
    salida.getvalue(),
    "Resultado_Operaciones.xlsx"
)
