import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ==================================
# CONFIGURACION PAGINA
# ==================================

st.set_page_config(
    page_title="Panel de Control Operaciones",
    layout="wide"
)

st.title("📊 Panel de Control Operaciones")

# ==================================
# CONTRASEÑA
# ==================================

PASSWORD = "Operaciones2026"

password = st.text_input(
    "🔐 Ingrese la contraseña",
    type="password"
)

if password != PASSWORD:
    st.warning(
        "Debe ingresar una contraseña válida para acceder al tablero."
    )
    st.stop()

# ==================================
# MENSAJE
# ==================================

st.markdown("""
### Bienvenido

Cargue el reporte de Zehux para visualizar:

✅ Casos entre 1 y 4 días

✅ Casos entre 5 y 6 días

✅ Casos con más de 6 días

✅ Días en Operaciones

✅ Días en Otras Áreas
""")

# ==================================
# CARGA ARCHIVO
# ==================================

archivo = st.file_uploader(
    "📂 Cargar archivo Excel",
    type=["xlsx"]
)

if archivo:

    df = pd.read_excel(archivo)

    st.success("✅ Archivo cargado correctamente")

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
    # VALIDACION DE COLUMNAS
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

    df["Clasificacion"] = df[
        "Dias Operaciones"
    ].apply(clasificar)

    # ==================================
    # INDICADORES
    # ==================================

    total_casos = len(df)

    casos_1_4 = len(
        df[
            df["Clasificacion"]
            == "🟢 1 a 4 días"
        ]
    )

    casos_5_6 = len(
        df[
            df["Clasificacion"]
            == "🟡 5 a 6 días"
        ]
    )

    casos_mas_6 = len(
        df[
            df["Clasificacion"]
            == "🔴 Más de 6 días"
        ]
    )

    cumplimiento = round(
        (
            casos_1_4 / total_casos
        ) * 100,
        2
    ) if total_casos > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Casos",
        total_casos
    )

    col2.metric(
        "🟢 Casos 1-4 días",
        casos_1_4
    )

    col3.metric(
        "🟡 Casos 5-6 días",
        casos_5_6
    )

    col4.metric(
        "🔴 Casos > 6 días",
        casos_mas_6
    )

    col5.metric(
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
        title="Distribución de Casos por Rango"
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
        if c in df.columns
    ]

    st.dataframe(
        top10[columnas_top10],
        use_container_width=True
    )

    if "Radicado" in top10.columns:

        fig2 = px.bar(
            top10,
            x="Radicado",
            y="Dias Operaciones",
            text="Dias Operaciones",
            title="Top 10 Casos con Mayor Tiempo en Operaciones"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    # ==================================
    # CASOS CRITICOS
    # ==================================

    st.subheader(
        "🔴 Casos con Más de 6 Días"
    )

    criticos = df[
        df["Dias Operaciones"] > 6
    ]

    if len(criticos) > 0:

        columnas_criticos = [
            c for c in [
                "Radicado",
                "Razon Social",
                "Fecha Radicado",
                "Fecha Asignacion",
                "Dias Operaciones",
                "Dias Otras Areas"
            ]
            if c in df.columns
        ]

        st.dataframe(
            criticos[columnas_criticos],
            use_container_width=True
        )

    else:

        st.success(
            "✅ No existen casos mayores a 6 días."
        )

    st.divider()

    # ==================================
    # RESULTADOS
    # ==================================

    st.subheader(
        "📋 Archivo Procesado"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    # ==================================
    # DESCARGAR EXCEL
    # ==================================

    archivo_salida = BytesIO()

    with pd.ExcelWriter(
        archivo_salida,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Resultados",
            index=False
        )

    st.download_button(
        label="📥 Descargar Excel Procesado",
        data=archivo_salida.getvalue(),
        file_name="Resultado_Operaciones.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
