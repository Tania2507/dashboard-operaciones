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

# Copia para tendencia histórica
df_original = df.copy()

# ==================================
# FECHA RADICADO Y FILTRO
# ==================================

if "Fecha Radicado" in df.columns:

    df["Fecha Radicado"] = pd.to_datetime(
        df["Fecha Radicado"],
        errors="coerce"
    )

    df_original["Fecha Radicado"] = pd.to_datetime(
        df_original["Fecha Radicado"],
        errors="coerce"
    )

    df["Mes Radicado"] = (
        df["Fecha Radicado"]
        .dt.strftime("%Y-%m")
    )

    df_original["Mes Radicado"] = (
        df_original["Fecha Radicado"]
        .dt.strftime("%Y-%m")
    )

    st.sidebar.header("📅 Filtros")

    meses = sorted(
        df["Mes Radicado"]
        .dropna()
        .unique()
    )

    mes_seleccionado = st.sidebar.selectbox(
        "Mes de Radicado",
        ["Todos"] + list(meses)
    )

    if mes_seleccionado != "Todos":

        df = df[
            df["Mes Radicado"]
            == mes_seleccionado
        ]

        st.info(
            f"Mostrando información del mes: {mes_seleccionado}"
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

# Se adiciona 1 día correspondiente
# al día de radicación

df["Dias Operaciones"] = (
    df[operaciones]
    .sum(axis=1)
    .add(1)
    .round(2)
)

df["Dias Otras Areas"] = (
    df[otras_areas]
    .sum(axis=1)
    .round(2)
)

# Total DC que se mostrará en las tablas

df["Total DC"] = df["Dias Operaciones"]

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
# FILTRO POR ESTADO (COLUMNA AN)
# ==================================

col_estado = df.columns[39]  # AN

df_finalizados = df[
    df[col_estado]
    .astype(str)
    .str.upper()
    .str.strip()
    == "FINALIZADO"
]

df_pendientes = df[
    df[col_estado]
    .astype(str)
    .str.upper()
    .str.strip()
    .isin(["ABIERTO", "DEVUELTO"])
]
st.subheader("✅ Casos Finalizados")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Finalizados",
    len(df_finalizados)
)

c2.metric(
    "🟢 1-4 días",
    len(df_finalizados[df_finalizados["Clasificacion"] == "🟢 1 a 4 días"])
)

c3.metric(
    "🟡 5-6 días",
    len(df_finalizados[df_finalizados["Clasificacion"] == "🟡 5 a 6 días"])
)

c4.metric(
    "🔴 > 6 días",
    len(df_finalizados[df_finalizados["Clasificacion"] == "🔴 Más de 6 días"])
)
st.subheader("📂 Casos Abiertos y Devueltos")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Abiertos/Devueltos",
    len(df_pendientes)
)

c2.metric(
    "🟢 1-4 días",
    len(df_pendientes[df_pendientes["Clasificacion"] == "🟢 1 a 4 días"])
)

c3.metric(
    "🟡 5-6 días",
    len(df_pendientes[df_pendientes["Clasificacion"] == "🟡 5 a 6 días"])
)

c4.metric(
    "🔴 > 6 días",
    len(df_pendientes[df_pendientes["Clasificacion"] == "🔴 Más de 6 días"])
)
st.divider()

# ==================================
# GRAFICO FINALIZADOS
# ==================================

resumen_finalizados = pd.DataFrame({
    "Clasificacion": [
        "🟢 1 a 4 días",
        "🟡 5 a 6 días",
        "🔴 Más de 6 días"
    ],
    "Cantidad": [
        len(df_finalizados[df_finalizados["Clasificacion"] == "🟢 1 a 4 días"]),
        len(df_finalizados[df_finalizados["Clasificacion"] == "🟡 5 a 6 días"]),
        len(df_finalizados[df_finalizados["Clasificacion"] == "🔴 Más de 6 días"])
    ]
})

# ==================================
# GRAFICO ABIERTOS + DEVUELTOS
# ==================================

resumen_pendientes = pd.DataFrame({
    "Clasificacion": [
        "🟢 1 a 4 días",
        "🟡 5 a 6 días",
        "🔴 Más de 6 días"
    ],
    "Cantidad": [
        len(df_pendientes[df_pendientes["Clasificacion"] == "🟢 1 a 4 días"]),
        len(df_pendientes[df_pendientes["Clasificacion"] == "🟡 5 a 6 días"]),
        len(df_pendientes[df_pendientes["Clasificacion"] == "🔴 Más de 6 días"])
    ]
})

col1, col2 = st.columns(2)

with col1:
    fig_finalizados = px.pie(
        resumen_finalizados,
        names="Clasificacion",
        values="Cantidad",
        hole=0.55,
        title="Distribución Casos Finalizados"
    )

    st.plotly_chart(
        fig_finalizados,
        use_container_width=True
    )

with col2:
    fig_pendientes = px.pie(
        resumen_pendientes,
        names="Clasificacion",
        values="Cantidad",
        hole=0.55,
        title="Distribución Casos Abiertos y Devueltos"
    )

    st.plotly_chart(
        fig_pendientes,
        use_container_width=True
    )
# ==================================
# TENDENCIA MENSUAL
# ==================================

if "Mes Radicado" in df_original.columns:

    st.subheader(
        "📈 Tendencia Mensual de Radicados"
    )

    tendencia = (
        df_original
        .groupby("Mes Radicado")
        .size()
        .reset_index(name="Cantidad")
    )

    fig_mes = px.bar(
        tendencia,
        x="Mes Radicado",
        y="Cantidad",
        text="Cantidad",
        title="Cantidad de Casos por Mes de Radicación"
    )

    st.plotly_chart(
        fig_mes,
        use_container_width=True
    )
# ==================================
# TOTAL DC
# ==================================

df["Total DC"] = df["Dias Operaciones"]

# ==================================
# COLUMNAS A MOSTRAR
# ==================================

columnas_tabla = [

    col for col in [

        "Radicado",
        "Fecha Radicado",
        "Usuario",

        "DC Validacion SARLAFT",
        "DC Sucursal",
        "DC Sistemas",
        "DC Renovacion",
        "DC Imagine",
        "DC Configuracion",
        "DC Expedicion",
        "DC Actualizacion FCC y Anexos",
        "DC Pendiente Blanket",
        "DC Facturacion Vencida",
        "DC Vigencia Futura",
        "DC Area Tecnica",

        "Total DC"

    ]

    if col in df.columns

]

# ==================================
# CASOS ENTRE 5 Y 6 DIAS
# ==================================

st.subheader(
    "🟡 Casos entre 5 y 6 días en Operaciones"
)

casos_5_6 = df[
    (df["Dias Operaciones"] > 4)
    &
    (df["Dias Operaciones"] <= 6)
]

if len(casos_5_6) > 0:

    st.dataframe(

        casos_5_6[
            columnas_tabla
        ]
        .sort_values(
            by="Total DC",
            ascending=False
        ),

        use_container_width=True

    )

else:

    st.success(
        "✅ No existen casos entre 5 y 6 días."
    )

# ==================================
# CASOS CON MAS DE 6 DIAS
# ==================================

st.subheader(
    "🔴 Casos con más de 6 días en Operaciones"
)

casos_criticos = df[
    df["Dias Operaciones"] > 6
]

if len(casos_criticos) > 0:

    st.dataframe(

        casos_criticos[
            columnas_tabla
        ]
        .sort_values(
            by="Total DC",
            ascending=False
        ),

        use_container_width=True

    )

else:

    st.success(
        "✅ No existen casos mayores a 6 días."
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
