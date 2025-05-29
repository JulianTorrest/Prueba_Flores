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

## Problemática 10 (Ajustada): Rendimiento Promedio de Tallos por Postcosecha por Jornada

if not df_produccion.empty and 'Postcosecha' in df_produccion.columns and 'FechaJornada' in df_produccion.columns and 'Tallos' in df_produccion.columns:
    df_produccion_clean = df_produccion.copy()
    df_produccion_clean['Postcosecha'] = df_produccion_clean['Postcosecha'].astype(str)

    # Sumar tallos por Postcosecha y jornada
    rendimiento_diario_postcosecha = df_produccion_clean.groupby(['Postcosecha', 'FechaJornada'])['Tallos'].sum().reset_index()
    rendimiento_diario_postcosecha.rename(columns={'Tallos': 'Tallos_Producidos'}, inplace=True)

    # Calcular el promedio de rendimiento por Postcosecha a lo largo del tiempo
    rendimiento_promedio_por_postcosecha = rendimiento_diario_postcosecha.groupby('Postcosecha')['Tallos_Producidos'].mean().sort_values(ascending=False).head(15).reset_index()

    if not rendimiento_promedio_por_postcosecha.empty:
        st.subheader('Top 15 Postcosechas por Rendimiento Promedio de Tallos por Jornada')
        fig_rendimiento_bar, ax_rendimiento_bar = plt.subplots(figsize=(14, 8))
        sns.barplot(x='Postcosecha', y='Tallos_Producidos', hue='Postcosecha', data=rendimiento_promedio_por_postcosecha, palette='Spectral', legend=False, ax=ax_rendimiento_bar)
        ax_rendimiento_bar.set_title('Top 15 Postcosechas por Rendimiento Promedio de Tallos por Jornada')
        ax_rendimiento_bar.set_xlabel('Postcosecha')
        ax_rendimiento_bar.set_ylabel('Promedio de Tallos Producidos por Jornada')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Formatear el eje Y
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax_rendimiento_bar.yaxis.set_major_formatter(formatter)
        ax_rendimiento_bar.ticklabel_format(style='plain', axis='y')

        st.pyplot(fig_rendimiento_bar)
        plt.close(fig_rendimiento_bar) # CERRAR LA FIGURA

        st.subheader('Distribución del Rendimiento Diario de Tallos por Postcosecha')
        # Opcional: Para ver la distribución general del rendimiento diario por Postcosecha
        fig_hist, ax_hist = plt.subplots(figsize=(10, 6))
        sns.histplot(rendimiento_diario_postcosecha['Tallos_Producidos'], bins=30, kde=True, color='skyblue', ax=ax_hist)
        ax_hist.set_title('Distribución del Rendimiento Diario de Tallos por Postcosecha')
        ax_hist.set_xlabel('Tallos Producidos por Jornada')
        ax_hist.set_ylabel('Frecuencia')
        plt.tight_layout()

        # Formatear el eje X (Tallos Producidos)
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax_hist.xaxis.set_major_formatter(formatter)
        ax_hist.ticklabel_format(style='plain', axis='x')

        st.pyplot(fig_hist)
        plt.close(fig_hist) # CERRAR LA FIGURA

    else:
        st.info("No hay datos de producción con información de Postcosecha y FechaJornada para calcular el rendimiento.")
else:
    st.warning("No se puede realizar el análisis de 'Rendimiento Promedio de Tallos por Postcosecha por Jornada'. Asegúrate de que `df_produccion` esté cargado y contenga las columnas 'Tallos', 'Postcosecha' y 'FechaJornada'.")

st.success("¡Todos los análisis se han intentado generar! Revisa los mensajes de información y advertencia para cualquier detalle.")

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

## Problemática 6: Fincas con Mayores Índices de Calidad No Conforme (NCC)

if not df_ncc.empty and 'Tallos' in df_ncc.columns and 'Finca' in df_ncc.columns:
    # Priorizar CausaAgrupada, si no, usar Causa
    if 'CausaAgrupada' in df_ncc.columns and not df_ncc['CausaAgrupada'].isnull().all():
        ncc_finca_causa = df_ncc.groupby(['Finca', 'CausaAgrupada'])['Tallos'].sum().nlargest(10).reset_index()
        x_col = 'CausaAgrupada'
    elif 'Causa' in df_ncc.columns:
        ncc_finca_causa = df_ncc.groupby(['Finca', 'Causa'])['Tallos'].sum().nlargest(10).reset_index()
        x_col = 'Causa'
    else:
        st.warning("No se encontraron las columnas 'CausaAgrupada' o 'Causa' en `df_ncc` para este análisis.")
        ncc_finca_causa = pd.DataFrame() # Vaciar el DataFrame si no hay columnas de causa válidas

    if not ncc_finca_causa.empty:
        st.subheader('Top 10 Causas de Calidad No Conforme (NCC) por Finca')
        fig_ncc, ax_ncc = plt.subplots(figsize=(14, 8))
        # Usamos 'Finca' para hue para ver las diferentes fincas, y x_col para la causa.
        sns.barplot(x=x_col, y='Tallos', hue='Finca', data=ncc_finca_causa, palette='tab10', ax=ax_ncc)
        ax_ncc.set_title('Top 10 Causas de Calidad No Conforme (NCC) por Finca')
        ax_ncc.set_xlabel('Causa de Calidad No Conforme')
        ax_ncc.set_ylabel('Total de Tallos No Conformes')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Finca', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # Formatear el eje Y para evitar notación científica y mostrar enteros
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax_ncc.yaxis.set_major_formatter(formatter)
        ax_ncc.ticklabel_format(style='plain', axis='y')

        st.pyplot(fig_ncc)
    else:
        st.info("No se encontraron datos de Calidad No Conforme (NCC) para analizar por Finca y Causa.")
else:
    st.warning("No se puede realizar el análisis de 'Fincas con Mayores Índices de Calidad No Conforme (NCC)'. Asegúrate de que `df_ncc` esté cargado y contenga las columnas 'Tallos', 'Finca', y al menos 'Causa' o 'CausaAgrupada'.")

## Problemática 7: Comportamiento de Tallos por Ramo por Variedad

if not df_produccion.empty and 'Tallos' in df_produccion.columns and 'Ramos' in df_produccion.columns and 'Variedad' in df_produccion.columns:
    # Evitar división por cero y manejar casos donde Ramos es 0
    df_produccion_clean = df_produccion[df_produccion['Ramos'] > 0].copy()

    if not df_produccion_clean.empty:
        df_produccion_clean['Tallos_por_Ramo'] = df_produccion_clean['Tallos'] / df_produccion_clean['Ramos']

        # Calcular el promedio de tallos por ramo por variedad
        tallos_por_ramo_por_variedad = df_produccion_clean.groupby('Variedad')['Tallos_por_Ramo'].mean().sort_values(ascending=False).reset_index()

        # Podemos visualizar las 7 primeras y las 8 últimas para ver los extremos
        top_low_varieties = pd.concat([tallos_por_ramo_por_variedad.head(7), tallos_por_ramo_por_variedad.tail(8)])

        if not top_low_varieties.empty:
            st.subheader('Promedio de Tallos por Ramo por Variedad (Extremos)')
            fig_tpr, ax_tpr = plt.subplots(figsize=(14, 7))
            sns.barplot(x='Variedad', y='Tallos_por_Ramo', hue='Variedad', data=top_low_varieties, palette='coolwarm', legend=False, ax=ax_tpr)
            ax_tpr.set_title('Promedio de Tallos por Ramo por Variedad (Extremos)')
            ax_tpr.set_xlabel('Variedad')
            ax_tpr.set_ylabel('Promedio de Tallos por Ramo')
            plt.xticks(rotation=60, ha='right')
            plt.tight_layout()
            st.pyplot(fig_tpr)
        else:
            st.info("No hay datos suficientes para mostrar el promedio de Tallos por Ramo por Variedad.")
    else:
        st.info("No hay datos de producción con Ramos > 0 para calcular Tallos por Ramo.")
else:
    st.warning("No se puede realizar el análisis de 'Comportamiento de Tallos por Ramo por Variedad'. Asegúrate de que `df_produccion` esté cargado y contenga las columnas 'Tallos', 'Ramos', y 'Variedad'.")

st.success("Análisis completado. ¡Explora tus datos!")

# Problematica 8: Causas Principales de Pérdida (NCP)
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

## Problemática 09: Impacto de Mala Marcación en Descarte de Tallos (NCP)

if not df_ncp.empty and 'Causa' in df_ncp.columns and 'Tallos' in df_ncp.columns:
    causas_marcacion_incorrecta = ['MALA MARCACION', 'MARCACIÓN INCORRECTA', 'ETIQUETA MAL IMPRESA']

    # Asegurarse de que la columna 'Causa' es string para un filtrado seguro
    df_ncp_clean = df_ncp.copy()
    df_ncp_clean['Causa'] = df_ncp_clean['Causa'].astype(str)

    tallos_por_mala_marcacion = df_ncp_clean[df_ncp_clean['Causa'].isin(causas_marcacion_incorrecta)]['Tallos'].sum()
    total_tallos_ncp = df_ncp_clean['Tallos'].sum()

    if total_tallos_ncp > 0:
        porcentaje_mala_marcacion = (tallos_por_mala_marcacion / total_tallos_ncp) * 100
        st.write(f"Total de tallos descartados por problemas de marcación: **{int(tallos_por_mala_marcacion)}** tallos")
        st.write(f"Porcentaje de tallos descartados por problemas de marcación sobre el total de NCP: **{porcentaje_mala_marcacion:.2f}%**")

        # Visualización de la proporción (gráfico de pastel simple)
        if tallos_por_mala_marcacion > 0:
            otros_ncp = total_tallos_ncp - tallos_por_mala_marcacion
            data_pie = pd.DataFrame({'Tipo': ['Problemas de Marcación', 'Otros Descartados'], 'Tallos': [tallos_por_mala_marcacion, otros_ncp]})

            st.subheader('Proporción de Tallos Descartados por Problemas de Marcación (NCP)')
            fig_pie_marcacion, ax_pie_marcacion = plt.subplots(figsize=(8, 8))
            ax_pie_marcacion.pie(data_pie['Tallos'], labels=data_pie['Tipo'], autopct='%1.1f%%', startangle=90, colors=['#FF9999', '#66B2FF'])
            ax_pie_marcacion.set_title('Proporción de Tallos Descartados por Problemas de Marcación (NCP)')
            ax_pie_marcacion.axis('equal')
            plt.tight_layout()
            st.pyplot(fig_pie_marcacion)
            plt.close(fig_pie_marcacion) # CERRAR LA FIGURA
        else:
            st.info("No se encontraron tallos descartados por problemas de marcación específicos.")
    else:
        st.info("No hay tallos registrados en NCP para analizar problemas de marcación.")
else:
    st.warning("No se puede realizar el análisis de 'Impacto de Mala Marcación'. Asegúrate de que `df_ncp` esté cargado y contenga las columnas 'Causa' y 'Tallos'.")

## Problemática 10 (Ajustada): Rendimiento Promedio de Tallos por Postcosecha por Jornada

if not df_produccion.empty and 'Postcosecha' in df_produccion.columns and 'FechaJornada' in df_produccion.columns and 'Tallos' in df_produccion.columns:
    df_produccion_clean = df_produccion.copy()
    df_produccion_clean['Postcosecha'] = df_produccion_clean['Postcosecha'].astype(str)

    # Sumar tallos por Postcosecha y jornada
    rendimiento_diario_postcosecha = df_produccion_clean.groupby(['Postcosecha', 'FechaJornada'])['Tallos'].sum().reset_index()
    rendimiento_diario_postcosecha.rename(columns={'Tallos': 'Tallos_Producidos'}, inplace=True)

    # Calcular el promedio de rendimiento por Postcosecha a lo largo del tiempo
    rendimiento_promedio_por_postcosecha = rendimiento_diario_postcosecha.groupby('Postcosecha')['Tallos_Producidos'].mean().sort_values(ascending=False).head(15).reset_index()

    if not rendimiento_promedio_por_postcosecha.empty:
        st.subheader('Top 15 Postcosechas por Rendimiento Promedio de Tallos por Jornada')
        fig_rendimiento_bar, ax_rendimiento_bar = plt.subplots(figsize=(14, 8))
        sns.barplot(x='Postcosecha', y='Tallos_Producidos', hue='Postcosecha', data=rendimiento_promedio_por_postcosecha, palette='Spectral', legend=False, ax=ax_rendimiento_bar)
        ax_rendimiento_bar.set_title('Top 15 Postcosechas por Rendimiento Promedio de Tallos por Jornada')
        ax_rendimiento_bar.set_xlabel('Postcosecha')
        ax_rendimiento_bar.set_ylabel('Promedio de Tallos Producidos por Jornada')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Formatear el eje Y
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax_rendimiento_bar.yaxis.set_major_formatter(formatter)
        ax_rendimiento_bar.ticklabel_format(style='plain', axis='y')

        st.pyplot(fig_rendimiento_bar)
        plt.close(fig_rendimiento_bar) # CERRAR LA FIGURA

        st.subheader('Distribución del Rendimiento Diario de Tallos por Postcosecha')
        # Opcional: Para ver la distribución general del rendimiento diario por Postcosecha
        fig_hist, ax_hist = plt.subplots(figsize=(10, 6))
        sns.histplot(rendimiento_diario_postcosecha['Tallos_Producidos'], bins=30, kde=True, color='skyblue', ax=ax_hist)
        ax_hist.set_title('Distribución del Rendimiento Diario de Tallos por Postcosecha')
        ax_hist.set_xlabel('Tallos Producidos por Jornada')
        ax_hist.set_ylabel('Frecuencia')
        plt.tight_layout()

        # Formatear el eje X (Tallos Producidos)
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax_hist.xaxis.set_major_formatter(formatter)
        ax_hist.ticklabel_format(style='plain', axis='x')

        st.pyplot(fig_hist)
        plt.close(fig_hist) # CERRAR LA FIGURA

    else:
        st.info("No hay datos de producción con información de Postcosecha y FechaJornada para calcular el rendimiento.")
else:
    st.warning("No se puede realizar el análisis de 'Rendimiento Promedio de Tallos por Postcosecha por Jornada'. Asegúrate de que `df_produccion` esté cargado y contenga las columnas 'Tallos', 'Postcosecha' y 'FechaJornada'.")

st.success("¡Todos los análisis se han intentado generar! Revisa los mensajes de información y advertencia para cualquier detalle.")

## Problemática 11 (Ajustada): Rendimiento Promedio de Tallos por Postcosecha por Jornada

if not df_produccion.empty and 'Postcosecha' in df_produccion.columns and 'FechaJornada' in df_produccion.columns and 'Tallos' in df_produccion.columns:
    df_produccion_clean = df_produccion.copy()
    df_produccion_clean['Postcosecha'] = df_produccion_clean['Postcosecha'].astype(str)

    # Sumar tallos por Postcosecha y jornada
    rendimiento_diario_postcosecha = df_produccion_clean.groupby(['Postcosecha', 'FechaJornada'])['Tallos'].sum().reset_index()
    rendimiento_diario_postcosecha.rename(columns={'Tallos': 'Tallos_Producidos'}, inplace=True)

    # Calcular el promedio de rendimiento por Postcosecha a lo largo del tiempo
    rendimiento_promedio_por_postcosecha = rendimiento_diario_postcosecha.groupby('Postcosecha')['Tallos_Producidos'].mean().sort_values(ascending=False).head(15).reset_index()

    if not rendimiento_promedio_por_postcosecha.empty:
        st.subheader('Top 15 Postcosechas por Rendimiento Promedio de Tallos por Jornada')
        fig_rendimiento_bar, ax_rendimiento_bar = plt.subplots(figsize=(14, 8))
        sns.barplot(x='Postcosecha', y='Tallos_Producidos', hue='Postcosecha', data=rendimiento_promedio_por_postcosecha, palette='Spectral', legend=False, ax=ax_rendimiento_bar)
        ax_rendimiento_bar.set_title('Top 15 Postcosechas por Rendimiento Promedio de Tallos por Jornada')
        ax_rendimiento_bar.set_xlabel('Postcosecha')
        ax_rendimiento_bar.set_ylabel('Promedio de Tallos Producidos por Jornada')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Formatear el eje Y
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax_rendimiento_bar.yaxis.set_major_formatter(formatter)
        ax_rendimiento_bar.ticklabel_format(style='plain', axis='y')

        st.pyplot(fig_rendimiento_bar)

        st.subheader('Distribución del Rendimiento Diario de Tallos por Postcosecha')
        # Opcional: Para ver la distribución general del rendimiento diario por Postcosecha
        fig_hist, ax_hist = plt.subplots(figsize=(10, 6))
        sns.histplot(rendimiento_diario_postcosecha['Tallos_Producidos'], bins=30, kde=True, color='skyblue', ax=ax_hist)
        ax_hist.set_title('Distribución del Rendimiento Diario de Tallos por Postcosecha')
        ax_hist.set_xlabel('Tallos Producidos por Jornada')
        ax_hist.set_ylabel('Frecuencia')
        plt.tight_layout()

        # Formatear el eje X (Tallos Producidos)
        formatter = mticker.ScalarFormatter(useOffset=False, useMathText=False)
        formatter.set_scientific(False)
        ax_hist.xaxis.set_major_formatter(formatter)
        ax_hist.ticklabel_format(style='plain', axis='x')


        st.pyplot(fig_hist)

    else:
        st.info("No hay datos de producción con información de Postcosecha y FechaJornada para calcular el rendimiento.")
else:
    st.warning("No se puede realizar el análisis de 'Rendimiento Promedio de Tallos por Postcosecha por Jornada'. Asegúrate de que `df_produccion` esté cargado y contenga las columnas 'Postcosecha', 'FechaJornada', y 'Tallos'.")

st.success("Análisis completado. ¡Explora tus datos!")

st.subheader("Problemática 15: Porcentaje de Producción Descartada por Plagas/Enfermedades por Finca")

if not df_produccion.empty and not df_ncp.empty:
    # Definir las causas de plagas/enfermedades
    causas_plagas_enfermedades = [
        'DAÑO POR THRIPS', 'ACAROS', 'PRESENCIA DE THRIPS', 'MILDEO POLVOSO',
        'AFIDOS', 'MINADOR', 'MOSCA BLANCA', 'BOTRYTIS', 'ESCLEROTINEA',
        'PROBLEMA FITOSANITARIO', 'ROYA PARDA'
    ]

    # Asegurarse de que 'Finca' exista en ambos DataFrames y sean strings
    if 'Finca' in df_produccion.columns and 'Finca' in df_ncp.columns and 'Tallos' in df_produccion.columns and 'Tallos' in df_ncp.columns and 'Causa' in df_ncp.columns:
        df_produccion_clean_finca = df_produccion.copy()
        df_ncp_clean_finca = df_ncp.copy()

        df_produccion_clean_finca['Finca'] = df_produccion_clean_finca['Finca'].astype(str)
        df_ncp_clean_finca['Finca'] = df_ncp_clean_finca['Finca'].astype(str)
        df_ncp_clean_finca['Causa'] = df_ncp_clean_finca['Causa'].astype(str)


        # 1. Tallos descartados por plagas/enfermedades por finca (de df_ncp)
        # Usamos la columna 'Causa' para filtrar según la lista de causas específicas
        descartes_plagas_finca = df_ncp_clean_finca[df_ncp_clean_finca['Causa'].isin(causas_plagas_enfermedades)]
        descartes_plagas_finca_sum = descartes_plagas_finca.groupby('Finca')['Tallos'].sum().reset_index(name='TallosDescartadosPlagas')

        # 2. Producción total por finca (de df_produccion)
        produccion_total_finca = df_produccion_clean_finca.groupby('Finca')['Tallos'].sum().reset_index(name='ProduccionTotalFinca')

        # 3. Unir los datos
        merged_impacto = pd.merge(produccion_total_finca, descartes_plagas_finca_sum, on='Finca', how='left').fillna(0)

        # 4. Calcular el porcentaje
        # Evitar división por cero
        merged_impacto['Porcentaje_Descarte_Plagas'] = np.where(
            merged_impacto['ProduccionTotalFinca'] > 0,
            (merged_impacto['TallosDescartadosPlagas'] / merged_impacto['ProduccionTotalFinca']) * 100,
            0
        )

        merged_impacto = merged_impacto.sort_values(by='Porcentaje_Descarte_Plagas', ascending=False)

        if not merged_impacto.empty:
            st.write("### Impacto de Plagas/Enfermedades en la Producción por Finca:")
            st.dataframe(merged_impacto.head()) # Muestra la tabla en Streamlit

            fig, ax = plt.subplots(figsize=(12, 7)) # Crear la figura y los ejes
            sns.barplot(x='Finca', y='Porcentaje_Descarte_Plagas', hue='Finca', data=merged_impacto.head(10), palette='YlOrRd', legend=False, ax=ax)
            ax.set_title('Top 10 Fincas por % de Producción Descartada por Plagas/Enfermedades')
            ax.set_xlabel('Finca')
            ax.set_ylabel('Porcentaje Descartado por Plagas/Enfermedades (%)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig) # Muestra el gráfico en Streamlit
            plt.close(fig) # ¡CERRAR LA FIGURA!

        else:
            st.info("No hay datos suficientes para calcular el porcentaje de descarte por plagas/enfermedades por finca.")
    else:
        st.warning("Las columnas 'Finca', 'Tallos' o 'Causa' no se encontraron en los DataFrames necesarios para este análisis.")
else:
    st.warning("Uno o ambos DataFrames (df_produccion, df_ncp) están vacíos para este análisis.")

st.subheader("Problemática 15 (Mejorada): Porcentaje de Producción Descartada por Plagas/Enfermedades por Finca y Causa")

if not df_produccion.empty and not df_ncp.empty:
    # Definir las causas de plagas/enfermedades
    causas_plagas_enfermedades = [
        'DAÑO POR THRIPS', 'ACAROS', 'PRESENCIA DE THRIPS', 'MILDEO POLVOSO',
        'AFIDOS', 'MINADOR', 'MOSCA BLANCA', 'BOTRYTIS', 'ESCLEROTINEA',
        'PROBLEMA FITOSANITARIO', 'ROYA PARDA'
    ]

    # Determinar qué columna usar para las causas (priorizar CausaAgrupada)
    causa_col = 'CausaAgrupada' if 'CausaAgrupada' in df_ncp.columns and not df_ncp['CausaAgrupada'].isnull().all() else 'Causa'

    # Asegurarse de que las columnas necesarias existan y sean del tipo correcto
    if 'Finca' in df_produccion.columns and 'Finca' in df_ncp.columns and \
       'Tallos' in df_produccion.columns and 'Tallos' in df_ncp.columns and \
       'Causa' in df_ncp.columns: # 'Causa' es necesaria para el filtro inicial, luego usamos 'causa_col'

        df_produccion_temp = df_produccion.copy()
        df_ncp_temp = df_ncp.copy()

        df_produccion_temp['Finca'] = df_produccion_temp['Finca'].astype(str)
        df_ncp_temp['Finca'] = df_ncp_temp['Finca'].astype(str)
        df_ncp_temp['Causa'] = df_ncp_temp['Causa'].astype(str) # Asegurar que 'Causa' sea string para el filtro
        # Asegurar que la columna elegida para 'causa_col' también sea string si existe
        if causa_col in df_ncp_temp.columns:
            df_ncp_temp[causa_col] = df_ncp_temp[causa_col].astype(str)


        # 1. Tallos descartados por plagas/enfermedades por finca Y causa
        descartes_plagas_por_finca_causa = df_ncp_temp[df_ncp_temp['Causa'].isin(causas_plagas_enfermedades)].copy()

        if not descartes_plagas_por_finca_causa.empty:
            descartes_plagas_por_finca_causa_sum = descartes_plagas_por_finca_causa.groupby(['Finca', causa_col])['Tallos'].sum().reset_index(name='TallosDescartadosPlagas')

            # 2. Producción total por finca
            produccion_total_finca = df_produccion_temp.groupby('Finca')['Tallos'].sum().reset_index(name='ProduccionTotalFinca')

            # 3. Unir los datos para calcular el porcentaje
            # Merge descartes_plagas_por_finca_causa_sum con produccion_total_finca
            merged_impacto_causa = pd.merge(descartes_plagas_por_finca_causa_sum, produccion_total_finca, on='Finca', how='left').fillna(0)

            # 4. Calcular el porcentaje de cada causa de descarte de plagas sobre la producción total de la finca
            merged_impacto_causa['Porcentaje_Descarte_Plagas'] = np.where(
                merged_impacto_causa['ProduccionTotalFinca'] > 0,
                (merged_impacto_causa['TallosDescartadosPlagas'] / merged_impacto_causa['ProduccionTotalFinca']) * 100,
                0
            )

            # Filtrar para mostrar solo las fincas con algún descarte por plagas significativo
            # Puedes ajustar este umbral si quieres mostrar más o menos fincas
            merged_impacto_causa_filtered = merged_impacto_causa[merged_impacto_causa['Porcentaje_Descarte_Plagas'] > 0].copy()

            if not merged_impacto_causa_filtered.empty:
                # Opcional: Para evitar un gráfico con demasiadas fincas, selecciona las top N por porcentaje total
                # Calcula el porcentaje total de descarte por plagas por finca para ordenar
                finca_total_pct = merged_impacto_causa_filtered.groupby('Finca')['Porcentaje_Descarte_Plagas'].sum().sort_values(ascending=False).head(10).index
                merged_impacto_causa_filtered = merged_impacto_causa_filtered[merged_impacto_causa_filtered['Finca'].isin(finca_total_pct)]

                # Ordenar para la visualización en el gráfico
                # Esto asegura que las fincas se muestren en el orden del top por su porcentaje total
                merged_impacto_causa_filtered['Finca_Order'] = pd.Categorical(merged_impacto_causa_filtered['Finca'], categories=finca_total_pct, ordered=True)
                merged_impacto_causa_filtered = merged_impacto_causa_filtered.sort_values('Finca_Order')

                st.write("### Desglose del Impacto de Plagas/Enfermedades por Finca y Causa:")
                st.dataframe(merged_impacto_causa_filtered) # Muestra la tabla en Streamlit

                fig, ax = plt.subplots(figsize=(14, 8)) # Crea la figura y los ejes
                sns.barplot(
                    x='Finca_Order', # Usar la columna ordenada para el eje X
                    y='Porcentaje_Descarte_Plagas',
                    hue=causa_col, # <--- ¡Aquí se agrega el desglose por causa!
                    data=merged_impacto_causa_filtered,
                    palette='tab20', # Una paleta con muchos colores distintos para las causas
                    ax=ax # Pasa los ejes al gráfico
                )
                ax.set_title('Porcentaje de Producción Descartada por Plagas/Enfermedades por Finca y Causa')
                ax.set_xlabel('Finca')
                ax.set_ylabel('Porcentaje Descartado por Plagas/Enfermedades (%)')
                plt.xticks(rotation=45, ha='right')
                plt.legend(title='Causa de Descarte', bbox_to_anchor=(1.02, 1), loc='upper left') # Mueve la leyenda fuera del gráfico
                plt.tight_layout()
                st.pyplot(fig) # Muestra el gráfico en Streamlit
                plt.close(fig) # ¡Cierra la figura para liberar memoria!

            else:
                st.info("No se encontraron descartes de plagas/enfermedades con un porcentaje significativo para graficar después del filtrado.")
        else:
            st.info("No se encontraron tallos descartados por plagas/enfermedades en NCP para este análisis.")
    else:
        st.warning("Las columnas **'Finca'**, **'Tallos'** o **'Causa'** no se encontraron en los DataFrames necesarios para este análisis. Asegúrate de que `df_produccion` y `df_ncp` contengan estas columnas.")
else:
    st.warning("Uno o ambos DataFrames (**`df_produccion`**, **`df_ncp`**) están vacíos para este análisis. Asegúrate de que los datos se hayan cargado correctamente.")

st.subheader("Problemática 16: Relación entre Finca, Causas de Descarte (NCP) y Producto")

if not df_ncp.empty:
    # Columnas a usar
    causa_col = 'CausaAgrupada' if 'CausaAgrupada' in df_ncp.columns and not df_ncp['CausaAgrupada'].isnull().all() else 'Causa'

    # Priorizar ProductoMaestro, si no, usar Producto
    producto_col = 'ProductoMaestro' if 'ProductoMaestro' in df_ncp.columns and not df_ncp['ProductoMaestro'].isnull().all() else 'Producto'

    # Verificar que las columnas clave existan antes de proceder
    if 'Finca' in df_ncp.columns and producto_col in df_ncp.columns and causa_col in df_ncp.columns and 'Tallos' in df_ncp.columns:
        df_ncp_filtered = df_ncp[df_ncp['Tallos'] > 0].copy()

        # Asegurar que las columnas sean de tipo string para agrupación segura
        df_ncp_filtered['Finca'] = df_ncp_filtered['Finca'].astype(str)
        df_ncp_filtered[causa_col] = df_ncp_filtered[causa_col].astype(str)
        df_ncp_filtered[producto_col] = df_ncp_filtered[producto_col].astype(str)


        # Agrupar y sumar tallos
        ncp_finca_causa_producto = df_ncp_filtered.groupby(['Finca', causa_col, producto_col])['Tallos'].sum().reset_index()

        if not ncp_finca_causa_producto.empty:
            # Seleccionar las top N fincas por total de descartes para mejor legibilidad
            top_fincas = ncp_finca_causa_producto.groupby('Finca')['Tallos'].sum().nlargest(5).index.tolist() # Top 5 fincas
            ncp_finca_causa_producto_top = ncp_finca_causa_producto[ncp_finca_causa_producto['Finca'].isin(top_fincas)]

            if not ncp_finca_causa_producto_top.empty:
                st.write(f"### Top 5 Fincas con Descarte por Finca, Causa y {producto_col}:")
                st.dataframe(ncp_finca_causa_producto_top) # Muestra el DataFrame en Streamlit

                # Crear un FacetGrid para dividir por Finca
                # `plt.figure()` no se usa directamente con FacetGrid, pero el método `map_dataframe`
                # crea figuras implícitamente o utiliza la figura actual si se provee.
                # Para Streamlit, es mejor dejar que FacetGrid cree la figura y luego pasarla.
                g = sns.FacetGrid(ncp_finca_causa_producto_top, col='Finca', col_wrap=3, height=5, aspect=1.2, sharey=False)

                # Mapear un barplot para cada faceta
                g.map_dataframe(sns.barplot, x=causa_col, y='Tallos', hue=producto_col, palette='tab20')

                # Ajustar títulos y etiquetas
                g.set_axis_labels(f"Causa de Descarte ({causa_col})", "Tallos Descartados")
                g.set_titles(col_template="Finca: {col_name}") # Título más descriptivo para cada columna (finca)
                g.set_xticklabels(rotation=45, ha='right')
                g.add_legend(title=producto_col, bbox_to_anchor=(1.02, 1), loc='upper left') # Leyenda externa

                g.figure.suptitle(f'Tallos Descartados (NCP) por Finca, Causa y {producto_col}', y=1.02, fontsize=16) # Título general para la figura
                plt.tight_layout(rect=[0, 0, 1, 0.98]) # Ajusta el layout para dar espacio al suptitle y la leyenda

                st.pyplot(g.figure) # Muestra la figura completa generada por FacetGrid
                plt.close(g.figure) # ¡Cierra la figura para liberar memoria!

            else:
                st.info("No se encontraron descartes significativos en las fincas seleccionadas para el desglose.")
        else:
            st.info("No se encontraron descartes (NCP) con datos completos de Finca, Causa y Producto después de la agrupación.")
    else:
        st.warning(f"Las columnas **'Finca'**, **'Tallos'**, **'{producto_col}'** o **'{causa_col}'** no se encontraron en `df_ncp`. Asegúrate de que los nombres de las columnas son correctos.")
else:
    st.warning("`df_ncp` está vacío. Asegúrate de que los datos se hayan cargado correctamente para analizar la relación entre Finca, Causas de Descarte y Producto.")


st.subheader("Mapa de Calor: Porcentaje de Aceptación por Finca y Producto")

if not df_produccion.empty and not df_ncp.empty:
    # Priorizar ProductoMaestro, si no, usar Producto para ambos DataFrames
    producto_col_prod = 'ProductoMaestro' if 'ProductoMaestro' in df_produccion.columns and not df_produccion['ProductoMaestro'].isnull().all() else 'Producto'
    producto_col_ncp = 'ProductoMaestro' if 'ProductoMaestro' in df_ncp.columns and not df_ncp['ProductoMaestro'].isnull().all() else 'Producto'

    # Verificar que las columnas clave existan antes de proceder
    if 'Finca' in df_produccion.columns and producto_col_prod in df_produccion.columns and 'Tallos' in df_produccion.columns and \
       'Finca' in df_ncp.columns and producto_col_ncp in df_ncp.columns and 'Tallos' in df_ncp.columns:

        # Crear copias para evitar SettingWithCopyWarning
        df_produccion_temp = df_produccion.copy()
        df_ncp_temp = df_ncp.copy()

        # Asegurarse de que las columnas sean string
        df_produccion_temp['Finca'] = df_produccion_temp['Finca'].astype(str)
        df_produccion_temp[producto_col_prod] = df_produccion_temp[producto_col_prod].astype(str)
        df_ncp_temp['Finca'] = df_ncp_temp['Finca'].astype(str)
        df_ncp_temp[producto_col_ncp] = df_ncp_temp[producto_col_ncp].astype(str)

        # 1. Calcular la producción total por Finca y Producto
        produccion_total_agrupada = df_produccion_temp.groupby(['Finca', producto_col_prod])['Tallos'].sum().reset_index(name='ProduccionTotal')

        # 2. Calcular los descartes (NCP) por Finca y Producto
        descartes_ncp_agrupados = df_ncp_temp.groupby(['Finca', producto_col_ncp])['Tallos'].sum().reset_index(name='TallosDescartadosNCP')

        # 3. Unir ambos DataFrames para calcular la aceptación
        # Alinear los nombres de las columnas de producto para el merge
        descartes_ncp_agrupados.rename(columns={producto_col_ncp: producto_col_prod}, inplace=True)

        merged_data = pd.merge(
            produccion_total_agrupada,
            descartes_ncp_agrupados,
            on=['Finca', producto_col_prod],
            how='left'
        ).fillna(0) # Rellenar con 0 si no hay descartes para una combinación

        # 4. Calcular Tallos Aceptados y Porcentaje de Aceptación
        merged_data['TallosAceptados'] = merged_data['ProduccionTotal'] - merged_data['TallosDescartadosNCP']

        merged_data['PorcentajeAceptacion'] = np.where(
            merged_data['ProduccionTotal'] > 0,
            (merged_data['TallosAceptados'] / merged_data['ProduccionTotal']) * 100,
            0 # Si no hay producción, el porcentaje de aceptación es 0
        )

        # Opcional: Mostrar los datos procesados para depuración
        st.write("### Datos para el Mapa de Calor (Primeras Filas):")
        st.dataframe(merged_data.head())

        # Crear la tabla pivote para el mapa de calor del porcentaje de aceptación
        heatmap_data_aceptacion = merged_data.pivot_table(
            index='Finca',
            columns=producto_col_prod,
            values='PorcentajeAceptacion',
            fill_value=np.nan # Usar NaN para productos no producidos por una finca para distinguirlos visualmente
        )

        if not heatmap_data_aceptacion.empty:
            # Ajustar la altura de la figura dinámicamente, con un máximo razonable
            fig_height = min(12, max(6, len(heatmap_data_aceptacion) * 0.7)) # Mínimo 6, máximo 12
            fig_width = min(20, max(10, len(heatmap_data_aceptacion.columns) * 0.5)) # Ancho dinámico

            fig, ax = plt.subplots(figsize=(fig_width, fig_height)) # Crea la figura y los ejes
            sns.heatmap(
                heatmap_data_aceptacion,
                annot=True,      # Mostrar los valores en las celdas
                fmt=".1f",       # Formato de los números (un decimal)
                cmap="YlGnBu",   # Esquema de color diferente para contraste
                linewidths=.5,
                linecolor='black',
                cbar_kws={'label': 'Porcentaje de Aceptación (%)'}, # Leyenda de la barra de color
                ax=ax            # Pasa los ejes al gráfico
            )
            ax.set_title(f'Porcentaje de Aceptación de Tallos por Finca y {producto_col_prod}', fontsize=16)
            ax.set_xlabel(f'{producto_col_prod}', fontsize=14)
            ax.set_ylabel('Finca', fontsize=14)
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            st.pyplot(fig) # Muestra el gráfico en Streamlit
            plt.close(fig) # ¡Cierra la figura para liberar memoria!

        else:
            st.info("No se encontraron datos procesados para generar el mapa de calor de Porcentaje de Aceptación. Esto podría deberse a filtros o datos vacíos después de las uniones.")
    else:
        st.warning(f"Las columnas **'Finca'**, **'Tallos'**, o **'{producto_col_prod}'** / **'{producto_col_ncp}'** no se encontraron en `df_produccion` o `df_ncp`. Asegúrate de que los nombres de las columnas sean correctos y existan en ambos DataFrames.")
else:
    st.warning("Uno o ambos DataFrames (**`df_produccion`**, **`df_ncp`**) están vacíos para este análisis. Asegúrate de que los datos se hayan cargado correctamente.")
