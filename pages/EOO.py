# Python File for streamlit tools
# GUI APP for IIOT | Corona
# July-2023
# ----------------------------------------------------------------------------------------------------------------------
# Libraries
import time
import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
# Internal Function
from Analysis_Function import visual_tabla_dinam_EOO
from Sql_Function import obtener_data, get_data_range, excel_search_by_date

# Streamlit Setting
st.set_page_config(page_title="BMC-RA EOO",
                   initial_sidebar_state="collapsed",
                   page_icon="./assets/logo_corona.png",
                   layout="wide")
# ----------------------------------------------------------------------------------------------------------------------
# Initial page
st.title(' 📈 EGE - BMC RA - Corona')
st.markdown("""---""")

# st.divider()
st.header('1) Selección de BMC a visualizar')
seleccionBMC = st.radio('¿Qué Banco de colage para ver el EGE?',
                        ['BMC Tanques EGE', 'BMC Tapas EGE'], 0)
st.markdown("""---""")

# ----------------------------------------------------------------------------------------------------------------------
# Fecha configuracion
st.header('2) Selección de periodo a visualizar')
fecha_actual = datetime.date.today()
col1, col2 = st.columns(2)
with col1:
    sel_fecha = st.radio('¿Qué periodo de tiempo desea analizar?',
                         ('Por día', 'Por rango de días'), key='fecha')
    flag_download = False
with col2:
    # opciones por día
    if sel_fecha == 'Por día':
        sel_dia = st.date_input('¿Qué día desea analizar?', fecha_actual, key='dia')

        if sel_dia > datetime.date.today():
            st.error(
                f"Recuerda que el día seleccionado no puede ser superior al día actual que es: {fecha_actual}")
            st.stop()

        st.info(f'Analizaras el día {str(sel_dia)}')

    # Opciones por rangos de días
    if sel_fecha == 'Por rango de días':
        sel_dia_inicial = st.date_input('Selecciona el día inicial', fecha_actual - datetime.timedelta(days=1),
                                        key='dia_ini')
        sel_dia_final = st.date_input('Selecciona el día final', fecha_actual, key='dia_fin')

        if sel_dia_final <= sel_dia_inicial:
            st.error("Recuerda seleccionar una fecha inicial anterior a la fecha final!!!")
            st.stop()

        elif sel_dia_final > fecha_actual:
            st.error("Recuerda que la fecha final no puede ser superior a la fecha actual")
            st.stop()

        else:
            st.info(f"Analizaras un periodo de tiempo de {str((sel_dia_final - sel_dia_inicial).days + 1)} días.")
# st.divider()
st.markdown("""---""")
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Visualización de la información
st.header('3) Graficar información')
descargar = st.checkbox('Graficar', key='graficaBMC')
if descargar is True:
    with st.spinner('Descargando la información'):
        # Buscar dataFrame por la fecha o rango escogido
        if sel_fecha == 'Por día':
            df3, salud_list, salud_datos, title = obtener_data(sel_dia, seleccionBMC, flag_download)
            # Fecha para usar en descargar archivo de excel
            text_dia = str(sel_dia)

        elif sel_fecha == 'Por rango de días':
            df3, salud_list, salud_datos, title = get_data_range(sel_dia_inicial, sel_dia_final, seleccionBMC,
                                                                 flag_download)
            # Rango de fecha para usar en descargar archivo de excel
            text_dia = "desde_" + str(sel_dia_inicial) + "_hasta_" + str(sel_dia_final)

        c1, c2, c3 = st.columns(3)
        c1.success('Información descargada')
        c2.metric(label='Salud global de los datos', value=f"{salud_datos:.2f}%")
        # -----------------------------------------------------------------------------------------------------
        # Plot Tanques
        if seleccionBMC == 'BMC Tanques EGE':
            st.markdown(type(df3.fecha[0]))
            # SQL
            df = df3
            st.markdown("Tabla para ver datos de SQL")
            visual_tabla_dinam_EOO(df, key='sql')

            # Excel
            archivo = "C:/Users/nsgutierrez/OneDrive - " \
                      "Corona\Documentos/apps_corona/IIOT_BMC_RA/data_tiempo_programado/BMC.xlsx"
            df1 = excel_search_by_date(text_dia, archivo)
            st.markdown("Tabla para ver datos del Excel")
            visual_tabla_dinam_EOO(df1, 'archivo_excel')

            # Combinar los DataFrames en base a la columna "fecha"
            # df_combined = pd.merge(df, df1, on='fecha')

            # Opciones para ver resultados de las 3 disponibilidades
            # ----------------------------------------------------------------------------------------------------------
            st.markdown("Disponibilidad Intrinsica, alcanzada, etc")
            # visual_tabla_dinam_EOO(df_combined, key='comnbinadad')
            # Calcular la disponibilidad intrinsica y almacenar en una nueva columna
            disponibilidad_intrinsica = (((df1['horas_programadas_tanques'] * 60) - df['Averias_Tanques'].values[0]) / (
                    df1['horas_programadas_tanques'] * 60)) * 100
            disponibilidad_alcanzada = (((df1['horas_programadas_tanques'] * 60) - df['Averias_Tanques'].values[0] -
                                         df['Mtto_programado_Tanques'].values[0]) / (
                                                df1['horas_programadas_tanques'] * 60)) * 100

            d_operativa_generalizada = (((df1['horas_programadas_tanques'] * 60) - df['Averias_Tanques'].values[0] -
                                    df['Mtto_programado_Tanques'].values[0] - df['Lavado_moldes_Tanques'].values[0] -
                                    df['Paro_proceso_Tanques'].values[0] - df['Maq_NoProgramada_Tanques'].values[0] -
                                    df['Servicios_Tanques'].values[0]) / (df1['horas_programadas_tanques'] * 60)) * 100

            piezas_a_hacer = ((d_operativa_generalizada / 100) * df1['horas_programadas_tanques'] * 60 / df1[
                'ciclo_ideal_tanques']) * df1["moldes_tanques"] + df1['cavidades_tanques']

            rendimiento = (df1["piezas_fabricadas_tanques"] / piezas_a_hacer) * 100

            OEE = (d_operativa_generalizada / 100) * (rendimiento / 100) * (df1["calidad_tanques"]) * 100

            # Seleccionar las columnas "fecha" y "EGE"
            d = {'Fecha': df1['fecha'],
                 'Disponibilidad_Intrinsica': round(disponibilidad_intrinsica, 2),
                 "Disponibilidad_alcanzada": round(disponibilidad_alcanzada, 2),
                 "Disponibilidad_Operativa_Generalizada": round(d_operativa_generalizada, 2),
                 "piezas_a_hacer": round(piezas_a_hacer, 0),
                 "rendimiento": round(rendimiento, 2),
                 "OEE": round(OEE, 2)

                 }

            # Imprimir la tabla resultante
            df2 = pd.DataFrame(data=d)
            df_dis = df2
            visual_tabla_dinam_EOO(df_dis, key='tabla')

            # ----------------------------------------------------------------------------------------------------------
            # grafico barras horizontales
            st.markdown("Grafico barras horizontales de Disponibilidad")
            labels = ['Disponibilidad_Intrinsica', 'Disponibilidad_alcanzada', 'Disponibilidad_Operativa_Generalizada',
                      'OEE']
            values = \
                df2[['Disponibilidad_Intrinsica', 'Disponibilidad_alcanzada', 'Disponibilidad_Operativa_Generalizada',
                 'OEE']].iloc[0]

            # Crear la figura de la gráfica de barras horizontales
            fig = go.Figure()

            # Agregar los datos de las barras horizontales
            fig.add_trace(go.Bar(
                y=labels,  # Nombres de las categorías en el eje Y
                x=values,  # Valores en el eje X
                orientation='h'  # Configurar las barras horizontales
            ))

            # Configurar el rango del eje Y
            fig.update_xaxes(range=[0, 100])

            st.plotly_chart(fig, use_container_width=True)
            # Opciones de los 6 items planteados
            # ----------------------------------------------------------------------------------------------------------
            st.markdown("Tabla de los 6 items: cálculos")
            columna_df_excel = df["Averias_Tanques"].values[0]
            resultado = (columna_df_excel / (df1['horas_programadas_tanques'].values[0] *60))
            # st.markdown(resultado)
            # calculos para los 6 item
            Averias_Tanques = resultado
                # ((df["Averias_Tanques"]) / (df1["horas_programadas_tanques"] * 60))

            dejan_averias = (((df["Averias_Tanques"].values[0])) / (df1["ciclo_ideal_tanques"].values[0] * df1["moldes_tanques"].values[0] * df1[
                "cavidades_tanques"].values[0]))

            Mtto_programado_Tanques = (((df["Mtto_programado_Tanques"].values[0]) / (df1["horas_programadas_tanques"].values[0] * 60)))

            dejan_mmto = (((df["Mtto_programado_Tanques"].values[0])) / (
                    df1["ciclo_ideal_tanques"].values[0] * df1["moldes_tanques"].values[0] * df1["cavidades_tanques"].values[0]))

            Lavado_moldes_Tanques = (((df["Lavado_moldes_Tanques"].values[0]) / (df1["horas_programadas_tanques"].values[0] * 60)))

            dejan_lvd = (((df["Lavado_moldes_Tanques"].values[0])) / (df1["ciclo_ideal_tanques"].values[0] * df1["moldes_tanques"].values[0] * df1[
                "cavidades_tanques"].values[0]))

            Paro_proceso_Tanques = (((df["Paro_proceso_Tanques"]) / (df1["horas_programadas_tanques"] * 60)))

            dejan_paro = (((df["Paro_proceso_Tanques"].values[0])) / (df1["ciclo_ideal_tanques"].values[0] * df1["moldes_tanques"].values[0] * df1[
                "cavidades_tanques"].values[0]))
            Maq_NoProgramada_Tanques = ((
                    (df["Maq_NoProgramada_Tanques"].values[0]) / (df1["horas_programadas_tanques"].values[0] * 60)))

            dejan_maq = ((df["Maq_NoProgramada_Tanques"].values[0])) / (
                    df1["ciclo_ideal_tanques"].values[0] * df1["moldes_tanques"].values[0] * df1["cavidades_tanques"].values[0])

            Servicios_Tanques = (
                    ((df["Servicios_Tanques"].values[0]) / (df1["horas_programadas_tanques"].values[0] * 60)))

            dejan_serv = (((df["Servicios_Tanques"].values[0])) / (df1["ciclo_ideal_tanques"].values[0] * df1["moldes_tanques"].values[0] * df1[
                "cavidades_tanques"].values[0]))

            d = {'Fecha': df['fecha'],
                 'Tiempo_Averias': round(Averias_Tanques * 100, 0),
                 "dejan_averias": round(dejan_averias * 100, 0),

                 'Mtto_programado_Tanques': round(Mtto_programado_Tanques * 100, 0),
                 "dejan_mtto": round(dejan_mmto * 100, 0),

                 'Lavado_moldes_Tanques': round(Lavado_moldes_Tanques * 100, 0),
                 "dejan_lvd": round(dejan_lvd * 100, 0),

                 'Paro_proceso_Tanques': round(Paro_proceso_Tanques * 100, 0),
                 "dejan_paro_proceso": round(dejan_maq * 100, 0),

                 'Maq_NoProgramada_Tanques': round(Maq_NoProgramada_Tanques * 100, 0),
                 "dejan_maq": round(dejan_maq * 100, 0),

                 'Servicios_Tanques': round(Servicios_Tanques * 100, 0),
                 "dejan_servicios": round(dejan_serv * 100, 0),

                 }

            # Imprimir la tabla resultante
            df4 = pd.DataFrame(data=d)
            df_circular = df4
            visual_tabla_dinam_EOO(df_circular, key='items')
            # ----------------------------------------------------------------------------------------------------------

            # grafica circular para los 6 items
            st.markdown("6 items")
            labels = ['Tiempo_Averias', 'Mtto_programado_Tanques', 'Lavado_moldes_Tanques', 'Paro_proceso_Tanques',
                      'Maq_NoProgramada_Tanques', 'Servicios_Tanques']
            values = df_circular[['Tiempo_Averias', 'Mtto_programado_Tanques', 'Lavado_moldes_Tanques',
                                  'Paro_proceso_Tanques', 'Maq_NoProgramada_Tanques', 'Servicios_Tanques']].iloc[0]

            # pull is given as a fraction of the pie radius
            fig2 = go.Figure(data=[go.Pie(labels=labels, values=values)])

            st.plotly_chart(fig2, use_container_width=True)
