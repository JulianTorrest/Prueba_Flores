import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Mi Aplicación Streamlit con Datos de GitHub")

# --- Carga de archivos CSV ---
st.header("Archivos CSV")
try:
    url_ncc = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/NCC.csv"
    df_ncc = pd.read_csv(url_ncc)
    st.success("NCC.csv cargado exitosamente:")
    st.dataframe(df_ncc.head())
except Exception as e:
    st.error(f"Error al cargar NCC.csv: {e}")

try:
    url_ncp = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/NCP.csv"
    df_ncp = pd.read_csv(url_ncp)
    st.success("NCP.csv cargado exitosamente:")
    st.dataframe(df_ncp.head())
except Exception as e:
    st.error(f"Error al cargar NCP.csv: {e}")

# --- Carga de archivos Excel ---
st.header("Archivos Excel")
url_produccion_raw = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Produccion.xlsx"
url_causa_raw = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Causa%20agrupado.xlsx"

try:
    # Si tu archivo Excel tiene varias hojas, puedes especificar cual cargar con sheet_name
    df_produccion = pd.read_excel(url_produccion_raw)
    st.success("Produccion.xlsx cargado exitosamente:")
    st.dataframe(df_produccion.head())
except Exception as e:
    st.error(f"Error al cargar Produccion.xlsx. Asegúrate de que la URL raw es correcta y el archivo es accesible: {e}")

try:
    df_causa_agrupado = pd.read_excel(url_causa_raw)
    st.success("Causa agrupado.xlsx cargado exitosamente:")
    st.dataframe(df_causa_agrupado.head())
except Exception as e:
    st.error(f"Error al cargar Causa agrupado.xlsx. Asegúrate de que la URL raw es correcta y el archivo es accesible: {e}")

st.set_page_config(layout="wide") # Opcional: Para usar todo el ancho de la página
st.title("Análisis de Datos de Flores - Producción y Causas")

# --- Definir las URLs de los archivos en GitHub ---
# Asegúrate de que estas URLs raw sean correctas para tu repositorio
excel_file_produccion = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Produccion.xlsx"
excel_file_causa_agrupado = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Causa%20agrupado.xlsx"
csv_file_ncc = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/NCC.csv"
csv_file_ncp = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/NCP.csv"

# --- Cargar los DataFrames ---
st.header("Cargando y Procesando Datos...")

# Cargar Produccion.xlsx
try:
    df_produccion = pd.read_excel(excel_file_produccion)
    st.success("`Produccion.xlsx` cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar `Produccion.xlsx`: {e}")
    df_produccion = pd.DataFrame() # Asegura que df_produccion siempre sea un DataFrame

# --- Cargar y procesar 'Causa agrupado.xlsx' ---
# Parte 1: Tabla de mapeo de causas (Columnas B y C)
try:
    df_causa_mapeo = pd.read_excel(excel_file_causa_agrupado, skiprows=0, usecols='B:C')
    df_causa_mapeo.rename(columns={'CAUSAS': 'Causa', 'CAUSAS AGRUPADAS': 'CausaAgrupada'}, inplace=True)
    df_causa_mapeo = df_causa_mapeo.drop_duplicates().dropna(subset=['Causa'])
    df_causa_mapeo['Causa'] = df_causa_mapeo['Causa'].astype(str) # Convertir 'Causa' a string
    st.success("Tabla de mapeo de causas cargada y procesada correctamente.")
except Exception as e:
    st.error(f"Error al cargar la tabla de mapeo de causas de `Causa agrupado.xlsx`: {e}")
    df_causa_mapeo = pd.DataFrame()

# Parte 2: Tabla de inspección de plagas/enfermedades (Desde E3 hasta Qx)
try:
    column_names_inspeccion = [
        'FINCA_INSP', 'VARIEDAD_INSP', 'TALLOS_ENTRADA_INSP',
        'PORCENTAJE_TALLOS_INSPECCIONADOS', 'THRIPSS', 'ACAROS', 'LEPIDOPTEROS',
        'AFIDOS', 'MINADOR', 'MOSCA_BLANCA', 'BOTRYTIS', 'OTRO_PROBLEMA', 'OBSERVACIONES_INSP'
    ]
    df_inspeccion_causas = pd.read_excel(
        excel_file_causa_agrupado,
        header=2,
        usecols='E:Q',
        names=column_names_inspeccion
    )
    df_inspeccion_causas = df_inspeccion_causas.dropna(how='all')
    st.success("Tabla de inspección de plagas/enfermedades cargada correctamente.")
except Exception as e:
    st.error(f"Error al cargar la tabla de inspección de `Causa agrupado.xlsx`: {e}")
    df_inspeccion_causas = pd.DataFrame()

# Cargar NCC.csv
try:
    df_ncc = pd.read_csv(csv_file_ncc, delimiter=';')
    st.success("`NCC.csv` cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar `NCC.csv`: {e}")
    df_ncc = pd.DataFrame()

# Cargar NCP.csv
try:
    df_ncp = pd.read_csv(csv_file_ncp, delimiter=';')
    st.success("`NCP.csv` cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar `NCP.csv`: {e}")
    df_ncp = pd.DataFrame()

## Limpieza y Conversión de Datos

# Convertir columnas de fecha en formato datetime
for df in [df_produccion, df_ncc, df_ncp]:
    if not df.empty: # Solo procesar si el DataFrame no está vacío
        if 'FechaJornada' in df.columns:
            df['FechaJornada'] = pd.to_datetime(df['FechaJornada'], errors='coerce')
        if 'HoraSistema' in df.columns:
            df['HoraSistema'] = pd.to_datetime(df['HoraSistema'], errors='coerce').dt.time
        if 'Hora' in df.columns:
            df['Hora'] = pd.to_datetime(df['Hora'], errors='coerce').dt.time

        # Convertir 'Causa' a string explícitamente en todos los DFs relevantes
        if 'Causa' in df.columns:
            df['Causa'] = df['Causa'].astype(str)

# Asegurarse de que las columnas de cantidad sean numéricas
for df in [df_produccion, df_ncc, df_ncp]:
    if not df.empty: # Solo procesar si el DataFrame no está vacío
        for col in ['Ramos', 'Tallos']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

st.success("Limpieza y conversión de datos completada.")

## Uniendo DataFrames

# Unir la tabla de mapeo de causas (df_causa_mapeo) con 'Produccion', 'NCC' y 'NCP'
if not df_produccion.empty and not df_causa_mapeo.empty:
    df_produccion = pd.merge(df_produccion, df_causa_mapeo, on='Causa', how='left')
    st.info("`df_produccion` unido con `df_causa_mapeo`.")
else:
    st.warning("No se pudo unir `df_produccion` con `df_causa_mapeo` (uno o ambos están vacíos).")

if not df_ncc.empty and not df_causa_mapeo.empty:
    df_ncc = pd.merge(df_ncc, df_causa_mapeo, on='Causa', how='left')
    st.info("`df_ncc` unido con `df_causa_mapeo`.")
else:
    st.warning("No se pudo unir `df_ncc` con `df_causa_mapeo` (uno o ambos están vacíos).")

if not df_ncp.empty and not df_causa_mapeo.empty:
    df_ncp = pd.merge(df_ncp, df_causa_mapeo, on='Causa', how='left')
    st.info("`df_ncp` unido con `df_causa_mapeo`.")
else:
    st.warning("No se pudo unir `df_ncp` con `df_causa_mapeo` (uno o ambos están vacíos).")

## Verificación de Datos Cargados y Procesados

if not df_inspeccion_causas.empty:
    st.subheader("Primeras filas de la tabla de Inspección de Plagas/Enfermedades")
    st.dataframe(df_inspeccion_causas.head())
    st.subheader("Columnas de la tabla de Inspección de Plagas/Enfermedades")
    st.write(df_inspeccion_causas.columns.tolist())
else:
    st.warning("La tabla de Inspección de Plagas/Enfermedades está vacía o no se cargó correctamente.")

## Análisis y Visualizaciones

st.header("Análisis de Datos")

# Problematica 1: Baja Producción Total de Tallos
st.subheader("Producción Total de Tallos por Día")
if not df_produccion.empty and 'FechaJornada' in df_produccion.columns and 'Tallos' in df_produccion.columns:
    df_produccion_diaria = df_produccion.groupby('FechaJornada')['Tallos'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df_produccion_diaria, x='FechaJornada', y='Tallos', ax=ax)
    ax.set_title('Producción Total de Tallos por Día')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Total de Tallos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig) # Muestra el gráfico en Streamlit
else:
    st.warning("No hay datos de producción disponibles o las columnas necesarias no existen para el análisis de producción total de tallos.")

# Problematica 7: Causas Principales de Pérdida (NCP)
st.subheader("Causas Principales de Pérdida (NCP)")
if not df_ncp.empty and 'Tallos' in df_ncp.columns:
    if 'CausaAgrupada' in df_ncp.columns:
        top_causas_ncp = df_ncp.groupby('CausaAgrupada')['Tallos'].sum().sort_values(ascending=False).head(10)
        titulo = 'Top 10 Causas Agrupadas de Pérdida (NCP)'
    elif 'Causa' in df_ncp.columns: # Fallback a 'Causa' si 'CausaAgrupada' no existe
        top_causas_ncp = df_ncp.groupby('Causa')['Tallos'].sum().sort_values(ascending=False).head(10)
        titulo = 'Top 10 Causas de Pérdida (NCP)'
    else:
        st.warning("Las columnas 'CausaAgrupada' o 'Causa' no se encontraron en `df_ncp` para este análisis.")
        top_causas_ncp = pd.Series() # Crea una serie vacía para evitar errores

    if not top_causas_ncp.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(x=top_causas_ncp.index, y=top_causas_ncp.values, palette='magma', ax=ax)
        ax.set_title(titulo)
        ax.set_xlabel('Causa')
        ax.set_ylabel('Tallos Perdidos')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig) # Muestra el gráfico en Streamlit
    else:
        st.info("No hay datos para mostrar el top de causas de pérdida en NCP.")
else:
    st.warning("No hay datos de NCP disponibles o la columna 'Tallos' no existe para el análisis de causas de pérdida.")

st.markdown("---")
st.success("Análisis completado")


