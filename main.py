import streamlit as st
import pandas as pd

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

# Para archivos Excel en GitHub, necesitas usar la URL "raw" para acceder al contenido directamente.
# Las URLs que proporcionaste para los .xlsx son las de la interfaz web de GitHub, no las directas.
# Debes modificarlas para que apunten al contenido "raw".
# Aquí te muestro cómo sería la URL "raw" para Produccion.xlsx (asumiendo la misma estructura que los CSV):
# url_produccion_raw = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Produccion.xlsx"
# url_causa_raw = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Causa%20agrupado.xlsx"

# Vamos a intentar construir las URLs raw para los archivos Excel basándonos en la estructura de los CSV
# Es importante verificar si estas URLs raw son correctas en tu repositorio.
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


st.markdown("""
---
### Siguientes pasos:
Ahora que los DataFrames están cargados, puedes empezar a:
- **Analizar los datos:** Realizar operaciones de filtrado, agrupación, cálculos, etc.
- **Visualizar los datos:** Usar librerías como `matplotlib`, `seaborn` o las propias funciones de Streamlit para crear gráficos.
- **Construir interactividad:** Añadir widgets de Streamlit (sliders, selectboxes, etc.) para que los usuarios interactúen con los datos.
- **Combinar DataFrames:** Unir los DataFrames si tienen relaciones entre ellos.
""")
