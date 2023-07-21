# Python File for streamlit tools
# GUI APP for IIOT | Corona
# July-2023
# ----------------------------------------------------------------------------------------------------------------------
# Libraries
import pandas as pd
import streamlit as st
import datetime

# Internal Function
from Analysis_Function import find_analisis, visual_tabla_dinam
from Sql_Function import excel_search_by_date, excel_search_by_date_range, get_data_range, get_data_day
from Plotly_Function_BMC import bar_hor_eoo, graf_torta_items

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

# TODO: Reemplazar linea del archivo donde se va a guardar el archivo real que usaran los operarios para guardar datos
#  del EQE.
archivo = "./data_tiempo_programado/BMC.xlsx"
if descargar is True:
    with st.spinner('Descargando la información'):
        # Buscar dataFrame por la fecha o rango escogido
        if sel_fecha == 'Por día':
            # Consulto en la base de datos
            df = get_data_day(sel_dia, seleccionBMC, flag_download)
            # Consulto en el Excel
            text_dia = str(sel_dia)
            df1 = excel_search_by_date(sel_dia, archivo)
            # Fecha para usar en descargar archivo de excel

        elif sel_fecha == 'Por rango de días':
            df = get_data_range(sel_dia_inicial, sel_dia_final, seleccionBMC, flag_download)

            df_range = excel_search_by_date_range(sel_dia_inicial, sel_dia_final, archivo)
            # Rango de fecha para usar en descargar archivo de excel
            text_dia = "from_" + str(sel_dia_inicial) + "_to_" + str(sel_dia_final)

        c1, c2, c3 = st.columns(3)
        c1.success('Información descargada')
        # -----------------------------------------------------------------------------------------------------
        # Option Tanques EGE
        if seleccionBMC == 'BMC Tanques EGE':
            if sel_fecha == 'Por día':
                # Uno los dos df (sql + excel) para trabajar con uno solo
                df_total = pd.merge(df, df1, on='fecha')
                analisis_dis, analisis_item = find_analisis(df_total, seleccionBMC, text_dia)
                # Solo muestro el ultimo dato del df
                analisis_item = analisis_item.tail(1)
                analisis = analisis_dis
                # Disponibilidad tabla
                st.markdown("Tabla Disponibilidad + EQE")
                visual_tabla_dinam(analisis, key='disponibilidad', flag_fecha=2)

                # Grafica Disponibilidad
                st.markdown("Grafico Disponibilidad + EQE")
                fig = bar_hor_eoo(analisis)
                st.plotly_chart(fig, use_container_width=True)

                # Tabla 6 items
                st.markdown("Tabla de los 6 items: cálculos")
                visual_tabla_dinam(analisis_item, key='items', flag_fecha=2)

                # Grafica circular para los 6 items
                st.markdown("Grafico Torta 6 items perdida de tiempos [M]")
                fig = graf_torta_items(analisis_item)
                st.plotly_chart(fig, use_container_width=True)

            elif sel_fecha == 'Por rango de días':
                # Uno los dos df (sql + excel) para trabajar con uno solo
                df_total = pd.merge(df, df_range, on='fecha')
                analisis_dis, analisis_item = find_analisis(df_total, seleccionBMC, text_dia)

                # Solo muestro el ultimo dato del df
                analisis_item = analisis_item.tail(1)
                analisis = analisis_dis.tail(1)

                # Disponibilidad Tabla
                st.markdown("Tabla Disponibilidad + EQE")
                visual_tabla_dinam(analisis, key='disponibilidad', flag_fecha=2)

                # Grafica Disponibilidad
                st.markdown("Grafico Disponibilidad + EQE")
                fig = bar_hor_eoo(analisis)
                st.plotly_chart(fig, use_container_width=True)

                # 6 items Tabla
                st.markdown("Tabla de los 6 items: cálculos")
                visual_tabla_dinam(analisis_item, key='items', flag_fecha=2)

                # Grafica de torta para los 6 items
                st.markdown("Grafico Torta 6 items perdida de tiempos [M]")
                fig = graf_torta_items(analisis_item)
                st.plotly_chart(fig, use_container_width=True)

        elif seleccionBMC == 'BMC Tapas EGE':
            if sel_fecha == "Por día":
                # Uno los dos df (sql + excel) para trabajar con uno solo
                df_total = pd.merge(df, df1, on='fecha')
                analisis_dis, analisis_item = find_analisis(df_total, seleccionBMC, text_dia)

                # Solo muestro el ultimo dato del df
                analisis_item = analisis_item.tail(1)
                analisis = analisis_dis.tail(1)

                # Disponibilidad tabla
                st.markdown("Tabla Disponibilidad + EQE")
                visual_tabla_dinam(analisis, key='disponibilidad', flag_fecha=2)

                # Grafica Disponibilidad
                st.markdown("Grafico Disponibilidad + EQE")
                fig = bar_hor_eoo(analisis)
                st.plotly_chart(fig, use_container_width=True)

                # 6 items
                st.markdown("Tabla de los 6 items: cálculos")
                visual_tabla_dinam(analisis_item, key='unidos', flag_fecha=2)

                # grafica circular para los 6 items
                st.markdown("Grafico Torta 6 items perdida de tiempos [M]")
                fig = graf_torta_items(analisis_item)
                st.plotly_chart(fig, use_container_width=True)

            elif sel_fecha == 'Por rango de días':
                # Uno los dos df (sql + excel) para trabajar con uno solo
                df_total = pd.merge(df, df_range, on='fecha')
                analisis_dis, analisis_item = find_analisis(df_total, seleccionBMC, text_dia)
                # Solo muestro el ultimo dato del df
                analisis_item = analisis_item.tail(1)
                analisis = analisis_dis.tail(1)

                # Disponibilidad
                st.markdown("Tabla Disponibilidad + EQE")
                visual_tabla_dinam(analisis, key='total', flag_fecha=2)

                # Grafica Disponibilidad
                st.markdown("Grafico Disponibilidad + EQE")
                fig = bar_hor_eoo(analisis)
                st.plotly_chart(fig, use_container_width=True)

                # 6 items tabla
                st.markdown("Tabla de los 6 items: cálculos")
                visual_tabla_dinam(analisis_item, key='unidos', flag_fecha=2)

                # Grafica circular para los 6 items
                st.markdown("Grafico Torta 6 items perdida de tiempos [M]")

                fig = graf_torta_items(analisis_item)
                st.plotly_chart(fig, use_container_width=True)
