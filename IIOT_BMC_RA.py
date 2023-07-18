# Aplicación de BMC para RA con Python Streamlit
# IIOT BMC Ramos Arizpe en México
# 30-MARZO-2023
# ----------------------------------------------------------------------------------------------------------------------
# Libraries
import datetime

import pandas as pd
import numpy as np
import streamlit as st

from Plotly_Function_BMC import plot_html_bmc_tanques, plot_html_bmc_tapas, plot_html_pres_linea, plot_html_corrientes,\
    plot_tiempo_muerto, plot_bar_acum_tiempo_muerto
from Sql_Function import get_data_day, get_data_range, to_excel
from Analysis_Function import find_analisis, visual_tabla_dinam
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Configuracion para la página
st.set_page_config(page_title='IIOT-BMC_RA',
                   initial_sidebar_state='collapsed',
                   page_icon='./assets/logo_corona.png',
                   layout='wide')


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Initial config
st.title('📈 IIOT|Corona: BMC Ramos Arizpe México')
st.markdown("""---""")

# st.divider()
st.header('1) Selección de BMC a visualizar')
seleccionBMC = st.radio('¿Qué Banco de colage desea visualizar?',
                        ['BMC Tanques', 'BMC Tapas', 'Presión de linea', 'Corriente de elevadores'], 0)
st.markdown("""---""")
# st.divider()

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
            df, salud_list, salud_datos, title = get_data_day(sel_dia, seleccionBMC, flag_download)
            # Fecha para usar en descargar archivo de excel
            text_dia = str(sel_dia)
            
        elif sel_fecha == 'Por rango de días':
            df, salud_list, salud_datos, title = get_data_range(sel_dia_inicial, sel_dia_final, seleccionBMC,
                                                                flag_download)
            # Rango de fecha para usar en descargar archivo de excel
            text_dia = "desde_" + str(sel_dia_inicial) + "_hasta_" + str(sel_dia_final)
            
        c1, c2, c3 = st.columns(3)
        c1.success('Información descargada')
        c2.metric(label='Salud global de los datos', value=f"{salud_datos:.2f}%")
        # -----------------------------------------------------------------------------------------------------
        # Plot Tanques
        if seleccionBMC == 'BMC Tanques':
            st.header('BMC Ramos Arizpe Tanques')
            # Button to refresh the data
            if st.button('Refrescar gráfica', key='refrescar'):
                flag_download = True
                get_data_day.clear()
                get_data_range.clear()
                st.experimental_rerun()

            # Dibujar gráfica
            with st.spinner('Dibujando la información...'):
                fig = plot_html_bmc_tanques(df, title)
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("Descargar archivo"):
                # Converting to Excel file
                excel = to_excel(df[['PresprensadoTQ', 'PrespastaTQ', 'TempPasta', 'TempAgua', 'PresLineaBar']])
                # Button to export the data
                st.download_button(label='📥 Descargar datos como un archivo *.xlsx',
                                   data=excel, file_name=f'datos_BMC_RA_tanques_{text_dia}.xlsx')

        # -----------------------------------------------------------------------------------------------------
        # Plot Tapas
        elif seleccionBMC == 'BMC Tapas':
            st.header('BMC Ramos Arizpe Tapas')
            # Button to refresh the data
            if st.button('Refrescar gráfica', key='refrescar'):
                flag_download = True
                get_data_day.clear()
                get_data_range.clear()
                st.experimental_rerun()

            # Dibujar gráfica
            with st.spinner('Dibujando la información...'):
                fig = plot_html_bmc_tapas(df, title)
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("Descargar archivo"):
                # Converting to Excel file
                excel = to_excel(df[['Estado_Tapas', 'PresprensadoTP', 'PrespastaTP', 'TempPasta', 'TempAgua',
                                     'PresLineaBar']])
                # Button to export the data
                st.download_button(label='📥 Descargar datos como un archivo *.xlsx',
                                   data=excel, file_name=f'Datos_BMC_RA_tapas_{text_dia}.xlsx')
        # -----------------------------------------------------------------------------------------------------
        # Plot Presión de linea    
        elif seleccionBMC == 'Presión de linea':
            st.header('Ramos Arizpe Presión de linea')
            # Button to refresh the data
            if st.button('Refrescar gráfica', key='refrescar'):
                flag_download = True
                get_data_day.clear()
                get_data_range.clear()
                st.experimental_rerun()
                
            # Dibujar gráfica
            with st.spinner('Dibujando la información...'):
                fig = plot_html_pres_linea(df, title)
                st.plotly_chart(fig, use_container_width=True)
                
            with st.expander("Descargar archivo"):
                # Converting to Excel file
                excel = to_excel(df[['PresLinea']])
                # Button to export the data
                st.download_button(label='📥 Descargar datos como un archivo *.xlsx',
                                   data=excel, file_name=f'Datos_RA_PresLinea_{text_dia}.xlsx')
        # -----------------------------------------------------------------------------------------------------
        # Plot Corriente de elevadores
        elif seleccionBMC == 'Corriente de elevadores':
            st.header('Corriente de elevadores RA')
            # Button to refresh the data
            if st.button('Refrescar gráfica', key='refrescar'):
                flag_download = True
                get_data_day.clear()
                get_data_range.clear()
                st.experimental_rerun()

            # Dibujar gráfica
            with st.spinner('Dibujando la información...'):
                fig = plot_html_corrientes(df, title)
                st.plotly_chart(fig, use_container_width=True)

                col1, col2, col3 = st.columns(3)
                with col3:
                    st.markdown("Descripción del eje Y derecho")
                    st.markdown("1: Detenido 2: Subiendo 3: Bajando")

            with st.expander("Descargar archivo"):
                # Converting to Excel file
                excel = to_excel(df[['elevador_delantero_tanques', 'elevador_trasero_tanques',
                                     'elevador_delantero_tapas', 'elevador_trasero_tapas', 'TQ_ELV_DL', 'TQ_ELV_TR',
                                     'TP_ELV_DL', 'TP_ELV_TR']])
                # Button to export the data
                st.download_button(label='📥 Descargar datos como un archivo *.xlsx',
                                   data=excel, file_name=f'Datos_RA_corriente_{text_dia}.xlsx')
# ----------------------------------------------------------------------------------------------------------------------
# Analitica de la información cargada
st.markdown("""---""")
st.subheader("4| Analizar Información")
analizar = st.checkbox("Analizar", key="Analizar")
if analizar is True:
    if descargar is False:
        # Button to refresh the data
        if st.button("Refrescar Análisis", key="refrescar_analisis"):
            flag_download = True
            get_data_day.clear()
            get_data_range.clear()
            st.experimental_rerun()

        # Descargando la información
        with st.spinner('Descargando la información...'):
            if sel_fecha == 'Por día':
                df, salud_list, salud_datos, title = get_data_day(sel_dia, seleccionBMC, flag_download)
                text_dia = str(sel_dia)

            elif sel_fecha == 'Por rango de días':
                df, salud_list, salud_datos, title = get_data_range(sel_dia_inicial, sel_dia_final, seleccionBMC,
                                                                    flag_download)
                text_dia = "desde_" + str(sel_dia_inicial) + "_hasta_" + str(sel_dia_final)
            # ----------------------------------------------------------------------------------------------------------
            # Salud de los datos descargada
            c1, c2, c3 = st.columns(3)
            c1.success("Información descargada")
            c2.metric(label="Salud global de los datos", value="{:.2f}%".format(salud_datos))
    # Analizando la información
    with st.spinner('Analizando la información...'):
        # Ejecuto la función que analiza el DF descargado
        if seleccionBMC == 'BMC Tanques':
            # Definición del robot seleccionado
            Analisis_df_raw = find_analisis(df=df, sel_bmc=seleccionBMC, text_dia=text_dia, redownload=flag_download)
        elif seleccionBMC == 'BMC Tapas':
            Analisis_df_raw = find_analisis(df=df, sel_bmc=seleccionBMC, text_dia=text_dia, redownload=flag_download)

        # Visualizando la tabla
        visual_tabla_dinam(Analisis_df_raw, "analisis_table")
        # ----------------------------------------------------------------------------------------------------------
        # Reportes tiempos de espera entre ciclo
        st.subheader("4.1. Reportes Tiempos De Espera entre ciclos")
        # ----------------------------------------------------------------------------------------------------------
        # ANALIZANDO tiempos muertos entre procesos de esmaltados
        # ----------------------------------------------------------------------------------------------------------
        with st.expander("Ver reportes de tiempos de espera entre ciclos"):

            var_fecha = Analisis_df_raw.Fecha.unique()
            # Definiendo el dataset total de tiempos
            Analisis_tiempos = pd.DataFrame(columns=['Fecha_all', 'Fecha', 'Hora',
                                                     'Tiempo_Espera [m]', 'Tiempo_Espera [s]'])

            for elem in var_fecha:
                # Filtrando el analisis por fecha
                Analisis_df_raw_robot = Analisis_df_raw[Analisis_df_raw['Fecha'] == elem].copy()

                # Convertiendo a string
                Analisis_df_raw_robot.loc[:, "Fecha"] = Analisis_df_raw_robot["Fecha"].apply(lambda x: str(x))
                Analisis_df_raw_robot.loc[:, "Hora"] = Analisis_df_raw_robot["Hora"].apply(lambda x: str(x))

                # Creando la columna con fecha y hora Inicial del proceso
                Fecha_ini = Analisis_df_raw_robot["Fecha"] + ", " + Analisis_df_raw_robot["Hora"]
                Fecha_ini_2 = Analisis_df_raw_robot["Fecha"] + ", " + Analisis_df_raw_robot["Hora"]

                # Convirtiendo a tipo datetime
                Fecha_ini = pd.to_datetime(Fecha_ini, format="%Y-%m-%d, %H:%M:%S")

                # Convirtiendo la duración del ciclo en un timedelta.
                time_delta = pd.to_timedelta(Analisis_df_raw_robot["Tiempo_Ciclo_Estado [S]"], unit='s')

                # Calculando la fecha final
                Fecha_final = Fecha_ini + time_delta

                # Cortando las listas para restar la fecha final a la fecha inicial posterior
                Fecha_ini = Fecha_ini[1:]
                Fecha_final = Fecha_final[:-1]

                # Calculando tiempos de espera entre 2 procesos, en minutos y segundos
                tiempo_espera_s = []
                tiempo_espera_m = []
                for i in range(len(Fecha_ini)):
                    tiempo_espera_s.append((Fecha_ini.iloc[i] - Fecha_final.iloc[i]).total_seconds())
                    diferencia = (Fecha_ini.iloc[i] - Fecha_final.iloc[i]).total_seconds()
                    diferencia = round(diferencia/60, 2)
                    tiempo_espera_m.append(diferencia)

                # Descomponiendo la fecha_final en fecha y tiempo
                Hora_final = Fecha_final.apply(lambda x: x.time())
                Fecha = Fecha_final.apply(lambda x: x.date())

                # Creando el df de tiempos muertos
                Analisis_tiempos_aux = pd.DataFrame(list(zip(Fecha_ini_2, Fecha, Hora_final,
                                                             tiempo_espera_m, tiempo_espera_s)),
                                                    columns=['Fecha_all', 'Fecha', 'Hora',
                                                             'Tiempo_Espera [m]', 'Tiempo_Espera [s]'])

                # Guardando resultados en el dataset final de tiempos
                Analisis_tiempos = pd.concat([Analisis_tiempos, Analisis_tiempos_aux])
            # ----------------------------------------------------------------------------------------------------------
            # Plotly
            TITLE = 'Tiempo de espera Ciclo Prensado'
            fig = plot_tiempo_muerto(Analisis_tiempos, TITLE)
            st.plotly_chart(fig, use_container_width=True)
            # ----------------------------------------------------------------------------------------------------------
            m1, m2 = st.columns(2)
            with m1:
                # Filtro los datos mayores al tiempo maximo de traslación
                tipo_visual = st.markdown("Analizar total")
                # Visualizando la tabla
                visual_tabla_dinam(Analisis_tiempos, key='tabla')
            with m2:
                # Filtro los datos mayores al tiempo maximo de traslación
                transfer_time = st.number_input("¿Cuanto es el tiempo máximo de translación [s]?", 120)

                # Filtro el df para tener solo aquellos datos mayores al tiempo de transfer
                Analisis_tiempos_filter = Analisis_tiempos[Analisis_tiempos['Tiempo_Espera [s]'] > transfer_time].copy()

                # Elimino el tiempo muerto
                Analisis_tiempos_filter.loc[:, 'Tiempo_Espera [s]'] -= transfer_time
                # -------------------------------------------------------------------------------------------------
                TITLE_PLOT = "Acumulado Tiempo Muerto"
                fig = plot_bar_acum_tiempo_muerto(Analisis_tiempos_filter, TITLE_PLOT)
                st.plotly_chart(fig, use_container_width=True)
# ----------------------------------------------------------------------------------------------------------------------
