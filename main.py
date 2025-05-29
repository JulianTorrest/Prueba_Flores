import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker # Importar para formatear el eje Y

st.set_page_config(layout="wide")
st.title("Análisis de Datos de Flores - Producción y Causas")

# Definir las URLs de los archivos en GitHub
# Asegúrate de que estas URLs raw sean correctas para tu repositorio
excel_file_produccion = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Produccion.xlsx"
excel_file_causa_agrupado = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/Causa%20agrupado.xlsx"
csv_file_ncc = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/NCC.csv"
csv_file_ncp = "https://raw.githubusercontent.com/JulianTorrest/Prueba_Flores/refs/heads/main/NCP.csv"

# Cargar los DataFrames
st.header("Cargando y Procesando Datos...")

# Cargar Produccion.xlsx
try:
    df_produccion = pd.read_excel(excel_file_produccion)
    st.success("`Produccion.xlsx` cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar `Produccion.xlsx`: {e}")
    df_produccion = pd.DataFrame()

# Cargar y procesar 'Causa agrupado.xlsx'
# Parte 1: Tabla de mapeo de causas (Columnas B y C)
try:
    df_causa_mapeo = pd.read_excel(excel_file_causa_agrupado, skiprows=0, usecols='B:C')
    df_causa_mapeo.rename(columns={'CAUSAS': 'Causa', 'CAUSAS AGRUPADAS': 'CausaAgrupada'}, inplace=True)
    df_causa_mapeo = df_causa_mapeo.drop_duplicates().dropna(subset=['Causa'])
    df_causa_mapeo['Causa'] = df_causa_mapeo['Causa'].astype(str)
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
        header=2, # Asegúrate que este sea el encabezado correcto de tu tabla de inspección
        usecols='E:Q', # Asegúrate que estas sean las columnas correctas
        names=column_names_inspeccion
    )
    df_inspeccion_causas = df_inspeccion_causas.dropna(how='all')
    st.success("Tabla de inspección de plagas/enfermedades cargada correctamente.")
except Exception as e:
    st.error(f"Error al cargar la tabla de inspección de `Causa agrupado.xlsx`: {e}")
    df_inspeccion_causas = pd.DataFrame()

# Cargar NCC.csv
try:
    df_ncc = pd.read_csv(csv_file_ncc, sep=';', engine='python', on_bad_lines='skip')
    st.success("`NCC.csv` cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar `NCC.csv`: {e}. Se intentó cargar con `engine='python'` y `on_bad_lines='skip'`.")
    df_ncc = pd.DataFrame()

# Cargar NCP.csv
try:
    df_ncp = pd.read_csv(csv_file_ncp, sep=';', engine='python', on_bad_lines='skip')
    st.success("`NCP.csv` cargado correctamente.")
except Exception as e:
    st.error(f"Error al cargar `NCP.csv`: {e}. Se intentó cargar con `engine='python'` y `on_bad_lines='skip'`.")
    df_ncp = pd.DataFrame()

## Limpieza y Conversión de Datos

st.subheader("Limpieza y Conversión de Datos")

# Convertir columnas de fecha en formato datetime
for df in [df_produccion, df_ncc, df_ncp]:
    if not df.empty:
        if 'FechaJornada' in df.columns:
            df['FechaJornada'] = pd.to_datetime(df['FechaJornada'], errors='coerce')
        if 'HoraSistema' in df.columns:
            df['HoraSistema'] = pd.to_datetime(df['HoraSistema'], errors='coerce').dt.time
        if 'Hora' in df.columns:
            df['Hora'] = pd.to_datetime(df['Hora'], errors='coerce').dt.time

        if 'Causa' in df.columns:
            df['Causa'] = df['Causa'].astype(str)

# Asegurarse de que las columnas de cantidad sean numéricas
for df in [df_produccion, df_ncc, df_ncp]:
    if not df.empty:
        for col in ['Ramos', 'Tallos']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

st.success("Limpieza y conversión de datos completada.")

## Uniendo DataFrames

st.subheader("Uniendo DataFrames")

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

    # Formatear el eje Y para evitar notación científica y mostrar enteros
    formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
    formatter.set_scientific(False)
    ax.yaxis.set_major_formatter(formatter)
    ax.ticklabel_format(style='plain', axis='y') # Intenta un estilo 'plain' adicional

    st.pyplot(fig)
else:
    st.warning("No hay datos de producción disponibles o las columnas necesarias no existen para el análisis de producción total de tallos.")

# Problematica 2: Variedades/Productos con Mayor Tasa de Pérdida
st.subheader("Problemática 2: Variedades/Productos con Mayor Tasa de Pérdida")
if not df_produccion.empty and 'Variedad' in df_produccion.columns and 'Tallos' in df_produccion.columns \
   and not df_ncp.empty and 'Variedad' in df_ncp.columns and 'Tallos' in df_ncp.columns:

    # Usaremos 'Variedad' como clave, si 'Producto' es más relevante puedes cambiarlo
    produccion_por_item = df_produccion.groupby('Variedad')['Tallos'].sum().reset_index(name='ProduccionTallos')
    ncp_por_item = df_ncp.groupby('Variedad')['Tallos'].sum().reset_index(name='NCPTallos')

    merged_items = pd.merge(produccion_por_item, ncp_por_item, on='Variedad', how='left').fillna(0)

    merged_items['TasaPerdida_Porcentaje'] = (merged_items['NCPTallos'] / merged_items['ProduccionTallos']) * 100
    merged_items = merged_items[merged_items['ProduccionTallos'] > 0] # Excluir ítems sin producción

    variedades_alta_perdida = merged_items.sort_values(by='TasaPerdida_Porcentaje', ascending=False).head(10)

    if not variedades_alta_perdida.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(x='Variedad', y='TasaPerdida_Porcentaje', hue='Variedad', data=variedades_alta_perdida, palette='Reds_d', legend=False, ax=ax)
        ax.set_title('Top 10 Variedades con Mayor Tasa de Pérdida (NCP)')
        ax.set_xlabel('Variedad')
        ax.set_ylabel('Tasa de Pérdida (%)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig) # Muestra el gráfico en Streamlit
    else:
        st.info("No se encontraron variedades/productos con tasa de pérdida calculable para el análisis.")
else:
    st.warning("No se puede realizar el análisis de Tasa de Pérdida. Asegúrate de que `df_produccion` y `df_ncp` estén cargados y contengan las columnas 'Variedad' y 'Tallos'.")

# Problemática 3: Estacionalidad de Producción y Pérdidas de Tallos
st.subheader("Problemática 3: Estacionalidad de Producción y Pérdidas de Tallos")
if not df_produccion.empty and 'FechaJornada' in df_produccion.columns and 'Tallos' in df_produccion.columns \
   and not df_ncp.empty and 'FechaJornada' in df_ncp.columns and 'Tallos' in df_ncp.columns:

    # Aseguramos que 'FechaJornada' esté en formato datetime antes de extraer el mes
    if not pd.api.types.is_datetime64_any_dtype(df_produccion['FechaJornada']):
        df_produccion['FechaJornada'] = pd.to_datetime(df_produccion['FechaJornada'], errors='coerce')
    if not pd.api.types.is_datetime64_any_dtype(df_ncp['FechaJornada']):
        df_ncp['FechaJornada'] = pd.to_datetime(df_ncp['FechaJornada'], errors='coerce')

    # Eliminar filas con fechas nulas si se produjeron errores de conversión
    df_produccion.dropna(subset=['FechaJornada'], inplace=True)
    df_ncp.dropna(subset=['FechaJornada'], inplace=True)


    df_produccion['Mes'] = df_produccion['FechaJornada'].dt.month
    df_ncp['Mes'] = df_ncp['FechaJornada'].dt.month

    produccion_mensual = df_produccion.groupby('Mes')['Tallos'].sum().reset_index(name='TallosProducidos')
    ncp_mensual = df_ncp.groupby('Mes')['Tallos'].sum().reset_index(name='TallosPerdidos')

    produccion_perdida_mensual = pd.merge(produccion_mensual, ncp_mensual, on='Mes', how='outer').fillna(0)

    # Asegúrate de que las columnas numéricas sean int si son conteos
    produccion_perdida_mensual['TallosProducidos'] = produccion_perdida_mensual['TallosProducidos'].astype(int)
    produccion_perdida_mensual['TallosPerdidos'] = produccion_perdida_mensual['TallosPerdidos'].astype(int)

    # Convertir a formato 'long' para seaborn.lineplot
    produccion_perdida_mensual_melted = produccion_perdida_mensual.melt(id_vars='Mes', var_name='Tipo', value_name='Tallos')

    if not produccion_perdida_mensual_melted.empty:
        fig, ax = plt.subplots(figsize=(14, 7))
        sns.lineplot(data=produccion_perdida_mensual_melted, x='Mes', y='Tallos', hue='Tipo', marker='o', palette={'TallosProducidos': 'green', 'TallosPerdidos': 'red'}, ax=ax)
        ax.set_title('Estacionalidad de Producción y Pérdidas de Tallos')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Total de Tallos')
        plt.xticks(range(1, 13), ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
        plt.legend(title='Tipo de Movimiento')
        plt.tight_layout()

        # Formatear el eje Y para evitar notación científica y mostrar enteros
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax.yaxis.set_major_formatter(formatter)
        ax.ticklabel_format(style='plain', axis='y')

        st.pyplot(fig) # Muestra el gráfico en Streamlit
    else:
        st.info("No hay datos suficientes para mostrar la estacionalidad de producción y pérdidas.")
else:
    st.warning("No se puede realizar el análisis de Estacionalidad. Asegúrate de que `df_produccion` y `df_ncp` estén cargados y contengan las columnas 'FechaJornada' y 'Tallos'.")

st.success("Análisis completado")

## Problemática 4: ¿Qué Postcosechas o Fincas están Generando Más Descartes de Alta Calidad?

if not df_ncp.empty and 'Grado' in df_ncp.columns and 'Tallos' in df_ncp.columns:
    grados_alta_calidad = ['SUPER PREMIUM', 'PREMIUM', 'SELECT', 'FANCY']

    ncp_alta_calidad = df_ncp[df_ncp['Grado'].isin(grados_alta_calidad)]

    if not ncp_alta_calidad.empty:
        st.info(f"Se encontraron pérdidas de tallos en los grados de alta calidad definidos: **{', '.join(grados_alta_calidad)}**")

        if 'Postcosecha' in ncp_alta_calidad.columns:
            # Por Postcosecha
            perdida_alta_calidad_pc = ncp_alta_calidad.groupby('Postcosecha')['Tallos'].sum().sort_values(ascending=False).head(10).reset_index()
            if not perdida_alta_calidad_pc.empty:
                st.subheader('Tallos de Alta Calidad Perdidos (NCP) por Postcosecha')
                fig_pc, ax_pc = plt.subplots(figsize=(12, 7))
                sns.barplot(x='Postcosecha', y='Tallos', hue='Postcosecha', data=perdida_alta_calidad_pc, palette='viridis', legend=False, ax=ax_pc)
                ax_pc.set_title('Tallos de Alta Calidad Perdidos (NCP) por Postcosecha')
                ax_pc.set_xlabel('Postcosecha')
                ax_pc.set_ylabel('Tallos de Alta Calidad Perdidos')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig_pc)
            else:
                st.info("No hay datos de pérdidas de alta calidad por Postcosecha para mostrar.")
        else:
            st.warning("La columna 'Postcosecha' no se encontró en los datos de NCP para este análisis.")

        if 'Finca' in ncp_alta_calidad.columns:
            # Por Finca
            perdida_alta_calidad_finca = ncp_alta_calidad.groupby('Finca')['Tallos'].sum().sort_values(ascending=False).head(10).reset_index()
            if not perdida_alta_calidad_finca.empty:
                st.subheader('Tallos de Alta Calidad Perdidos (NCP) por Finca')
                fig_finca, ax_finca = plt.subplots(figsize=(12, 7))
                sns.barplot(x='Finca', y='Tallos', hue='Finca', data=perdida_alta_calidad_finca, palette='cividis', legend=False, ax=ax_finca)
                ax_finca.set_title('Tallos de Alta Calidad Perdidos (NCP) por Finca')
                ax_finca.set_xlabel('Finca')
                ax_finca.set_ylabel('Tallos de Alta Calidad Perdidos')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig_finca)
            else:
                st.info("No hay datos de pérdidas de alta calidad por Finca para mostrar.")
        else:
            st.warning("La columna 'Finca' no se encontró en los datos de NCP para este análisis.")
    else:
        st.info(f"No se encontraron pérdidas de tallos en los grados de alta calidad definidos: **{', '.join(grados_alta_calidad)}**")
else:
    st.warning("No se puede realizar el análisis de 'Descartes de Alta Calidad'. Asegúrate de que `df_ncp` esté cargado y contenga las columnas 'Grado' y 'Tallos'.")

## Problemática 5: ¿Qué Porcentaje de Nuestra Producción de Alto Grado está Siendo Descartado por Plagas/Enfermedades Específicas?

if not df_produccion.empty and not df_ncp.empty and 'Grado' in df_produccion.columns and 'Tallos' in df_produccion.columns \
   and 'Grado' in df_ncp.columns and 'Tallos' in df_ncp.columns and 'Causa' in df_ncp.columns:

    grados_alta_calidad = ['SUPER PREMIUM', 'PREMIUM', 'SELECT', 'FANCY']

    causas_plagas_enfermedades = [
        'DAÑO POR THRIPS', 'ACAROS', 'PRESENCIA DE THRIPS', 'MILDEO POLVOSO',
        'AFIDOS', 'MINADOR', 'MOSCA BLANCA', 'BOTRYTIS', 'ESCLEROTINEA',
        'PROBLEMA FITOSANITARIO', 'ROYA PARDA'
    ]

    produccion_alta_calidad_tallos = df_produccion[df_produccion['Grado'].isin(grados_alta_calidad)]['Tallos'].sum()

    if 'CausaAgrupada' in df_ncp.columns and not df_ncp['CausaAgrupada'].isnull().all():
        st.info("Usando 'CausaAgrupada' para identificar las causas de plagas/enfermedades en las pérdidas y para el eje X del gráfico.")
        ncp_alta_calidad_plagas_df = df_ncp[
            (df_ncp['Grado'].isin(grados_alta_calidad)) &
            (df_ncp['Causa'].isin(causas_plagas_enfermedades))
        ]
        campo_causa_final = 'CausaAgrupada'
    else:
        st.info("Usando 'Causa' directamente para identificar las causas de plagas/enfermedades en las pérdidas (CausaAgrupada no disponible o vacía).")
        ncp_alta_calidad_plagas_df = df_ncp[
            (df_ncp['Grado'].isin(grados_alta_calidad)) &
            (df_ncp['Causa'].isin(causas_plagas_enfermedades))
        ]
        campo_causa_final = 'Causa'

    ncp_alta_calidad_plagas = ncp_alta_calidad_plagas_df['Tallos'].sum()

    if produccion_alta_calidad_tallos > 0:
        porcentaje_perdida = (ncp_alta_calidad_plagas / produccion_alta_calidad_tallos) * 100
        st.write(f"Porcentaje de tallos de alta calidad descartados por plagas/enfermedades: **{porcentaje_perdida:.2f}%**")

        if not ncp_alta_calidad_plagas_df.empty:
            perdida_por_plaga_grado_alto = ncp_alta_calidad_plagas_df.groupby(campo_causa_final)['Tallos'].sum().sort_values(ascending=False).reset_index()

            if not perdida_por_plaga_grado_alto.empty:
                st.subheader('Tallos de Alta Calidad Perdidos por Causas de Plagas/Enfermedades')
                fig_plaga, ax_plaga = plt.subplots(figsize=(12, 7))
                sns.barplot(x=campo_causa_final, y='Tallos', hue=campo_causa_final, data=perdida_por_plaga_grado_alto, palette='Greens_d', legend=False, ax=ax_plaga)
                ax_plaga.set_title('Tallos de Alta Calidad Perdidos por Causas de Plagas/Enfermedades')
                ax_plaga.set_xlabel(f'Causa ({campo_causa_final})')
                ax_plaga.set_ylabel('Tallos Perdidos de Alta Calidad')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig_plaga)
            else:
                st.info("No se encontraron pérdidas de tallos de alta calidad por las causas de plagas/enfermedades definidas para el desglose.")
        else:
            st.info("No hay datos de pérdidas de alta calidad por plagas/enfermedades después del filtrado para mostrar el desglose.")
    else:
        st.info("No hay producción de tallos de alta calidad registrada para este análisis.")
else:
    st.warning("No se puede realizar el análisis de 'Porcentaje de Producción de Alto Grado Descartado por Plagas/Enfermedades Específicas'. Asegúrate de que `df_produccion` y `df_ncp` estén cargados y contengan las columnas 'Grado', 'Tallos' y 'Causa'.")

st.success("Análisis completado. ¡Explora tus datos!")

# Problematica 7: Causas Principales de Pérdida (NCP)
st.subheader("Causas Principales de Pérdida (NCP)")
if not df_ncp.empty and 'Tallos' in df_ncp.columns:
    if 'CausaAgrupada' in df_ncp.columns:
        top_causas_ncp = df_ncp.groupby('CausaAgrupada')['Tallos'].sum().sort_values(ascending=False).head(10)
        titulo = 'Top 10 Causas Agrupadas de Pérdida (NCP)'
    elif 'Causa' in df_ncp.columns:
        top_causas_ncp = df_ncp.groupby('Causa')['Tallos'].sum().sort_values(ascending=False).head(10)
        titulo = 'Top 10 Causas de Pérdida (NCP)'
    else:
        st.warning("Las columnas 'CausaAgrupada' o 'Causa' no se encontraron en `df_ncp` para este análisis.")
        top_causas_ncp = pd.Series()

    if not top_causas_ncp.empty:
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(x=top_causas_ncp.index, y=top_causas_ncp.values, palette='magma', ax=ax)
        ax.set_title(titulo)
        ax.set_xlabel('Causa')
        ax.set_ylabel('Tallos Perdidos')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No hay datos para mostrar el top de causas de pérdida en NCP.")
else:
    st.warning("No hay datos de NCP disponibles o la columna 'Tallos' no existe para el análisis de causas de pérdida.")

st.success("Análisis completado. ¡Explora tus datos!")
