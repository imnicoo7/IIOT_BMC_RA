# Python File function for streamlit tools
# Analysis function for IIOT | Colceramica
# 07-July-2023
# ----------------------------------------------------------------------------------------------------------------------
# Libraries
import datetime
import os

import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder


# ----------------------------------------------------------------------------------------------------------------------
# Function definition

def visual_tabla_dinam(df, key, flag_fecha=1):
    """
    Función para generar las tablas dinamicas que se visualizan
    INPUT:
        df: data frame a visualizar
        key: Llave distinta para el objeto de streamlit

    """
    # Copy dataframe
    df_aux = df.copy()

    # Definiendo la tabla de visualización
    gb = GridOptionsBuilder.from_dataframe(df_aux)
    gb.configure_side_bar()

    if flag_fecha == 1:
        df_aux['Fecha'] = pd.to_datetime(df_aux['Fecha'], format='%Y-%m-%d', exact=False)
        # df_aux['Fecha_planta'] = pd.to_datetime(df_aux['Fecha_planta'], format='%Y-%m-%d', exact=False)
        gb.configure_column("Fecha", type=["dateColumnFilter", "customDateTimeFormat"],
                            custom_format_string='yyyy-MM-dd', pivot=True)
        height = 400

    elif flag_fecha == 2:
        height = 200

    gb.configure_grid_options(domLayout='normal')
    gridoptions = gb.build()

    AgGrid(df_aux, editable=False, sortable=True, filter=True, resizable=True, height=height, width='50%',
           defaultWidth=3,
           theme="blue",  # "light", "dark", "blue", "material" # defaultWidth=3, fit_columns_on_grid_load=False,
           key=key, reload_data=True, gridOptions=gridoptions,
           enable_enterprise_modules=False)
    return


def round_np(x):
    """
    Función que redondea una  3 cifras
    """
    return np.round(x, 3)


def round_mt(x):
    """
    Función para pasar de segundos a minutos y redondear
    """
    return np.round(x / 60, 0)


def correcion_div_0(tiempo_variable):
    """
    Función que corrige el error que causa la división por 0 que se puede presentar cuando el tiempo de las variables
    es igual a 0 en analizar
    Problem: ZeroDivisionError: division by zero
    INPUT:
        tiempo_variable: tiempo de la variable
    OUTPUT:
        tiempo_variable: tiempo de la variable diferente de 0
    """
    if tiempo_variable == 0:
        tiempo_variable = 0.001

    return tiempo_variable


# @st.cache_data(experimental_allow_widgets=True, show_spinner=True)
@st.experimental_memo(suppress_st_warning=True, show_spinner=True)
def find_analisis(df, sel_bmc, text_dia, redownload=False):
    """
    Función que busca y carga el archivo de datos analizados o en su lugar analiza la data.
    INPUT:
        df: dataframe que contiene la serie de tiempo que se debe analizar
        sel_bmc: BMC de donde viene la información
        text_dia: Información en STR sobre la fecha o rango analizado
        redownload = Debe descargarse la data o buscar dentro de los archivos previamente descargados
    OUTPUT:
        analisis_df: dataframe con los datos
    """

    # Setting the folder where to search
    if text_dia[:4] == "desde":
        directory = './Data/Analizadas/'
        filenames = os.listdir(directory)
    else:
        directory = './Data/Analizadas/' + text_dia[:-3] + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filenames = os.listdir(directory)

    # Creo el nombre del archivo a buscar
    filename = 'analisis_' + sel_bmc + '_' + text_dia + '.csv'

    # BMC Tanques option
    if sel_bmc == 'BMC Tanques':
        if filename in filenames and redownload is False:
            analisis_df = pd.read_csv(directory + filename)
        else:
            analisis_df = analisis_ciclos_tanques(df=df, table=sel_bmc, periodo=text_dia)

    # BMC Tapas option
    elif sel_bmc == 'BMC Tapas':
        if filename in filenames and redownload is False:
            analisis_df = pd.read_csv(directory + filename)
        else:
            analisis_df = analisis_ciclos_tapas(df=df, table=sel_bmc, periodo=text_dia)

    # Calcular EOO Tanques
    elif sel_bmc == 'BMC Tanques EGE':
        if filename in filenames and redownload is False:
            analisis_df = pd.read_csv(directory + filename)
        else:
            analisis_df, analisis_item = analis_eoo_tanques(df=df)

        return analisis_df, analisis_item

    # Calcular EOO Tanques
    elif sel_bmc == 'BMC Tapas EGE':
        if filename in filenames and redownload is False:
            analisis_df = pd.read_csv(directory + filename)
        else:
            analisis_df, analisis_item = analis_eoo_tapas(df=df)
        return analisis_df, analisis_item

    return analisis_df


def analisis_variable(df, idx_variable, variable, flag_var, tiempo_var, total_var, max_var, aux):
    """
        Programa que analizara la serie de tiempo y entrega valores internos del ciclo
    """
    # Indica que inicio la variable
    if df.iloc[idx_variable][variable] > 0.5 and flag_var is True:

        # Existen datos, cambio aux a 1
        aux = 1
        # Diferencia en el tiempo
        if idx_variable > 0:
            diferencia_dato = df.index[idx_variable] - df.index[idx_variable - 1]
            # Acumulo la data del proceso
            tiempo_var += diferencia_dato.total_seconds()
            total_var += ((df.iloc[idx_variable][variable] + df.iloc[idx_variable - 1][
                variable]) / 2) * diferencia_dato.total_seconds()
        else:
            # Acumulo la data del proceso
            tiempo_var += 1
            total_var += df.iloc[idx_variable][variable]

        # Obtener maximo de la variable
        if max_var < df.iloc[idx_variable][variable]:
            max_var = df.iloc[idx_variable][variable]

    # Método para identificar que el proceso finalizo
    elif df.iloc[idx_variable - 1][variable] > 0.5 and df.iloc[idx_variable][variable] > 0.5 and flag_var is True:
        # Evito error de desborde
        if idx_variable + 1 > df.shape[0] - 1:
            flag_var = False
        else:
            if df.iloc[idx_variable + 1][variable] > 0.5:
                flag_var = False

    return tiempo_var, total_var, max_var, flag_var, aux


# @st.cache_data(experimental_allow_widgets=True, show_spinner=True)
@st.experimental_memo(suppress_st_warning=True, show_spinner=True)
def analisis_ciclos_tanques(df, periodo, table):
    """
       Programa que analiza la serie de tiempo y crea un df a partir de cada ciclo analizado
    """
    # Inicialización del DF
    analisis_df = pd.DataFrame(columns=["Fecha", 'Hora', 'Dia', 'Proceso_Completo',
                                        'Tiempo_Ciclo_Estado [S]',
                                        'Tiempo_Ciclo_Prensado [M]',
                                        "Max_Presion_Prensado [PSI]", "Promedio_Presion_Prensado [PSI]",
                                        'Tiempo_Ciclo_Llenado [M]',
                                        "Max_Presion_Llenado [PSI]", "Promedio_Presion_Llenado[PSI]",
                                        "Max_Temp_Agua [C]", "Prom_Temp_Agua [C]",
                                        "Max_Temp_Pasta [C]", "Prom_Temp_Pasta [C]",
                                        "Max_Pres_Linea [PSI]", "Prom_Pres_Linea [PSI]"])

    idx = 0
    count = 0
    print("Inicio proceso de analisis de la información")
    while idx < df.shape[0]:
        # ----------------------------------------------------------------------------
        # Inicializacion varibles
        # ----------------------------------------------------------------------------
        # variables para los tiempos que duran cada ciclo
        tiempo_ciclo = 0
        tiempo_pres_pren = 0
        tiempo_pres_llen = 0

        # presiones
        max_pred_pren = 0
        max_pred_llen = 0
        max_temp_agua = 0
        max_temp_pasta = 0
        max_pres_linea = 0

        total_pres_pren = 0
        total_pres_llen = 0
        total_temp_agua = 0
        total_temp_pasta = 0
        total_pres_linea = 0

        aux_pren = 0
        aux_llen = 0

        flag_entrada_salida_ciclo = 1
        flag_pres_pren = True
        flag_pres_llen = True
        total_flag = True

        if df.iloc[idx]['Estado_Tanques'] == 1:
            # Guardo la fecha de inicio del ciclo
            fecha_ini = df.index[idx].date()
            hora = df.index[idx].time()
            ndia = df.iloc[idx]["ndia"]
            # Mensajes de control
            print(fecha_ini, ' - ', hora, ' - ', df.PresprensadoTP[idx], ' - ', df.PrespastaTP[idx])

            while df.iloc[idx]['Estado_Tanques'] == 1:
                # Cuento el tiempo que la presion prensado es mayor a 1
                # Cuento el tiempo que el ciclo este activo
                if idx > 0:
                    # Acumulo data del proceso

                    diferencia_tiempo = df.index[idx] - df.index[idx - 1]
                    tiempo_ciclo += diferencia_tiempo.total_seconds()

                    total_temp_agua += ((df.iloc[idx]["TempAgua"] +
                                         df.iloc[idx - 1]["TempAgua"]) / 2) * diferencia_tiempo.total_seconds()

                    total_temp_pasta += ((df.iloc[idx]["TempPasta"] +
                                          df.iloc[idx - 1]["TempPasta"]) / 2) * diferencia_tiempo.total_seconds()

                    total_pres_linea += ((df.iloc[idx]["PresLinea"] +
                                          df.iloc[idx - 1]["PresLinea"]) / 2) * diferencia_tiempo.total_seconds()
                else:
                    # Acumulo la data del proceso
                    tiempo_ciclo += 1
                    total_temp_agua += df.iloc[idx]["TempAgua"]
                    total_temp_pasta += df.iloc[idx]["TempPasta"]
                    total_pres_linea += df.iloc[idx]["PresLinea"]

                # ------------------------------------------------------------------------
                # Calcular MAX y promedios
                if max_temp_agua < df.iloc[idx]["TempAgua"]:
                    max_temp_agua = df.iloc[idx]["TempAgua"]

                if max_temp_pasta < df.iloc[idx]["TempPasta"]:
                    max_temp_pasta = df.iloc[idx]["TempPasta"]

                if max_pres_linea < df.iloc[idx]["PresLinea"]:
                    max_pres_linea = df.iloc[idx]["PresLinea"]

                # Calcular variables internas del ciclo
                idx_var = idx
                while total_flag is True:
                    # llamo funcion para calcular procesos internos ya que no empiezan igual al estado
                    # -----------------------------------------------------------------------------------
                    tiempo_pres_pren, total_pres_pren, max_pred_pren, flag_pres_pren, aux_pren \
                        = analisis_variable(df, idx_var, "PresprensadoTQ", flag_pres_pren,
                                            tiempo_pres_pren, total_pres_pren, max_pred_pren, aux_pren)
                    # -----------------------------------------------------------------------------------
                    tiempo_pres_llen, total_pres_llen, max_pred_llen, flag_pres_llen, aux_llen \
                        = analisis_variable(df, idx_var, "PrespastaTQ", flag_pres_llen, tiempo_pres_llen,
                                            total_pres_llen, max_pred_llen, aux_llen)
                    # -----------------------------------------------------------------------------------
                    # Termina el ciclo en las funciones, coloco aux en 0
                    aux_pren = 0
                    aux_llen = 0
                    # Por si nunca empiezan los procesos durante el tiempo de estado o
                    if df.iloc[idx_var]['Estado_Tanques'] == 0:
                        if aux_pren == 0:
                            flag_pres_pren = False
                        if aux_llen == 0:
                            flag_pres_llen = False

                    # Logica para salir del while
                    if flag_pres_pren is False and flag_pres_llen is False:
                        total_flag = False
                    elif idx_var == df.shape[0] - 1:
                        total_flag = False

                    idx_var += 1
                # --------------------------------------------------------------------------------------------
                # Avanzo en el df
                idx += 1

                # Por si el df finaliza o inicia con el estado 1, es decir que se corto el proceso
                if idx >= df.shape[0]:
                    flag_entrada_salida_ciclo = 0
                    print("¡NO SE TIENEN DATOS SUFICIENTE DEL ULTIMO CICLO: "
                          "El proceso no ha finalizado!\n")
                    break  # Salir del ciclo para evitar un error
                elif idx - 1 == 0:
                    flag_entrada_salida_ciclo = -1
                    print("¡NO SE TIENEN DATOS SUFICIENTE DEL PRIMER CICLO: "
                          "El proceso no ha finalizado!\n")

            # Evitando la division por cero cuando el estado esta ON pero no hay presión
            tiempo_ciclo = correcion_div_0(tiempo_ciclo)
            tiempo_pres_pren = correcion_div_0(tiempo_pres_pren)
            tiempo_pres_llen = correcion_div_0(tiempo_pres_llen)

            # inserting the new data into the df analized
            analisis_df.loc[count] = [fecha_ini, hora, ndia, float(flag_entrada_salida_ciclo),
                                      float(tiempo_ciclo), round_mt((tiempo_pres_pren)), max_pred_pren,
                                      round_np((total_pres_pren / tiempo_pres_pren)),
                                      round((tiempo_pres_llen)), max_pred_llen,
                                      round_np((total_pres_llen / tiempo_pres_llen)),
                                      max_temp_agua, round_np((total_temp_agua / tiempo_ciclo)),
                                      max_temp_pasta, round_np((total_temp_pasta / tiempo_ciclo)),
                                      max_pres_linea, round_np((total_pres_linea / tiempo_ciclo))]
            count += 1
        else:
            idx += 1

    # Mensajes de control
    print("Finalizo correctamente")

    # Aseguro los datos como numericos
    float_columns = analisis_df.columns.values.tolist()[7:30]
    analisis_df[float_columns] = analisis_df[float_columns].apply(pd.to_numeric, errors='ignore')

    # Guardo el analisis realizado
    if periodo == str(datetime.date.today()):
        pass  # No guardar datos si el día seleccionado es el día actual del sistema
    else:
        # Checking and creating the folder
        if periodo[:4] == "from":
            analisis_df.to_csv('./Data/Analizadas/analisis_' + table + '_' + periodo + '.csv', index=False)
        else:
            folder = periodo[:-3]
            if not os.path.exists('./Data/Analizadas/' + folder):
                os.makedirs('./Data/Analizadas/' + folder)
            # Salvando el analisis
            analisis_df.to_csv('./Data/Analizadas/' + folder + '/analisis_' + table + '_' + periodo + '.csv',
                               index=False)

    return analisis_df


# @st.cache_data(experimental_allow_widgets=True, show_spinner=True)
@st.experimental_memo(suppress_st_warning=True, show_spinner=True)
def analisis_ciclos_tapas(df, periodo, table):
    """
       Programa que analiza la serie de tiempo y crea un df a partir de cada ciclo analizado
    """
    # Inicialización del DF
    analisis_df = pd.DataFrame(columns=["Fecha", 'Hora', 'Dia', 'Proceso_Completo',
                                        'Tiempo_Ciclo_Estado [S]',
                                        'Tiempo_Ciclo_Prensado [M]',
                                        "Max_Presion_Prensado [PSI]", "Promedio_Presion_Prensado [PSI]",
                                        'Tiempo_Ciclo_Llenado [M]',
                                        "Max_Presion_Llenado [PSI]", "Promedio_Presion_Llenado[PSI]",
                                        "Max_Temp_Agua [C]", "Prom_Temp_Agua [C]",
                                        "Max_Temp_Pasta [C]", "Prom_Temp_Pasta [C]",
                                        "Max_Pres_Linea [PSI]", "Prom_Pres_Linea [PSI]"])

    idx = 0
    count = 0
    print("Inicio proceso de analisis de la información")
    while idx < df.shape[0]:
        # ----------------------------------------------------------------------------
        # Inicializacion varibles
        # ----------------------------------------------------------------------------
        # variables para los tiempos que duran cada ciclo
        tiempo_ciclo = 0
        tiempo_pres_pren = 0
        tiempo_pres_llen = 0

        # presiones
        max_pred_pren = 0
        max_pred_llen = 0
        max_temp_agua = 0
        max_temp_pasta = 0
        max_pres_linea = 0

        total_pres_pren = 0
        total_pres_llen = 0
        total_temp_agua = 0
        total_temp_pasta = 0
        total_pres_linea = 0

        aux_pren = 0
        aux_llen = 0

        flag_entrada_salida_ciclo = 1
        flag_pres_pren = True
        flag_pres_llen = True
        total_flag = True

        if df.iloc[idx]['Estado_Tapas'] == 1:
            # Guardo la fecha de inicio del estado
            fecha_ini = df.index[idx].date()
            hora = df.index[idx].time()
            ndia = df.iloc[idx]["ndia"]
            # Mensajes de control
            print(fecha_ini, ' - ', hora, ' - ', df.PresprensadoTP[idx], ' - ', df.PrespastaTP[idx])

            while df.iloc[idx]['Estado_Tapas'] == 1:
                # Cuento el tiempo que la presion prensado es mayor a 1
                # Cuento el tiempo que el ciclo este activo
                if idx > 0:
                    # Acumulo data del proceso

                    diferencia_tiempo = df.index[idx] - df.index[idx - 1]
                    tiempo_ciclo += diferencia_tiempo.total_seconds()

                    total_temp_agua += ((df.iloc[idx]["TempAgua"] + df.iloc[idx - 1][
                        "TempAgua"]) / 2) * diferencia_tiempo.total_seconds()

                    total_temp_pasta += ((df.iloc[idx]["TempPasta"] + df.iloc[idx - 1][
                        "TempPasta"]) / 2) * diferencia_tiempo.total_seconds()

                    total_pres_linea += ((df.iloc[idx]["PresLinea"] + df.iloc[idx - 1][
                        "PresLinea"]) / 2) * diferencia_tiempo.total_seconds()
                else:
                    # Acumulo la data del proceso
                    tiempo_ciclo += 1
                    total_temp_agua += df.iloc[idx]["TempAgua"]
                    total_temp_pasta += df.iloc[idx]["TempPasta"]
                    total_pres_linea += df.iloc[idx]["PresLinea"]

                # ------------------------------------------------------------------------
                # Calcular MAX y promedios
                if max_temp_agua < df.iloc[idx]["TempAgua"]:
                    max_temp_agua = df.iloc[idx]["TempAgua"]

                if max_temp_pasta < df.iloc[idx]["TempPasta"]:
                    max_temp_pasta = df.iloc[idx]["TempPasta"]

                if max_pres_linea < df.iloc[idx]["PresLinea"]:
                    max_pres_linea = df.iloc[idx]["PresLinea"]

                # Calcular variables internas del ciclo
                idx_var = idx
                while total_flag is True:
                    # llamo funcion para calcular procesos internos ya que no empiezan igual al estado
                    # -----------------------------------------------------------------------------------
                    tiempo_pres_pren, total_pres_pren, max_pred_pren, flag_pres_pren, aux_pren \
                        = analisis_variable(df, idx_var, "PresprensadoTP", flag_pres_pren,
                                            tiempo_pres_pren, total_pres_pren, max_pred_pren, aux_pren)
                    # -----------------------------------------------------------------------------------
                    tiempo_pres_llen, total_pres_llen, max_pred_llen, flag_pres_llen, aux_llen \
                        = analisis_variable(df, idx_var, "PrespastaTP", flag_pres_llen, tiempo_pres_llen,
                                            total_pres_llen, max_pred_llen, aux_llen)
                    # -----------------------------------------------------------------------------------
                    # Termina el ciclo en las funciones, coloco aux en 0
                    aux_pren = 0
                    aux_llen = 0
                    # Por si nunca empiezan los procesos durante el tiempo de estado o
                    if df.iloc[idx_var]['Estado_Tapas'] == 0:
                        if aux_pren == 0:
                            flag_pres_pren = False
                        if aux_llen == 0:
                            flag_pres_llen = False

                    # Logica para salir del while
                    if flag_pres_pren is False and flag_pres_llen is False:
                        total_flag = False
                    elif idx_var == df.shape[0] - 1:
                        total_flag = False

                    idx_var += 1
                # --------------------------------------------------------------------------------------------
                # Avanzo en el df
                idx += 1

                # Por si el df finaliza o inicia con el estado 1, es decir que se corto el proceso
                if idx >= df.shape[0]:
                    flag_entrada_salida_ciclo = 0
                    print("¡NO SE TIENEN DATOS SUFICIENTE DEL ULTIMO CICLO: "
                          "El proceso no ha finalizado!\n")
                    break  # Salir del ciclo para evitar un error
                elif idx - 1 == 0:
                    flag_entrada_salida_ciclo = -1
                    print("¡NO SE TIENEN DATOS SUFICIENTE DEL PRIMER CICLO: "
                          "El proceso no ha finalizado!\n")

            # Evitando la division por cero cuando el estado esta ON pero no hay presión
            tiempo_ciclo = correcion_div_0(tiempo_ciclo)
            tiempo_pres_pren = correcion_div_0(tiempo_pres_pren)
            tiempo_pres_llen = correcion_div_0(tiempo_pres_llen)

            # inserting the new data into the df analized
            analisis_df.loc[count] = [fecha_ini, hora, ndia, float(flag_entrada_salida_ciclo), float(tiempo_ciclo),
                                      round_mt((tiempo_pres_pren)), max_pred_pren,
                                      round_np((total_pres_pren / tiempo_pres_pren)),  # prensado
                                      round_mt((tiempo_pres_llen)), max_pred_llen,  # llenado
                                      round_np((total_pres_llen / tiempo_pres_llen)),
                                      max_temp_agua, round_np((total_temp_agua / tiempo_ciclo)),  # temp agua
                                      max_temp_pasta, round_np((total_temp_pasta / tiempo_ciclo)),  # temp pasta
                                      max_pres_linea, round_np((total_pres_linea / tiempo_ciclo))]  # pres linea
            count += 1
        else:
            idx += 1

    # Mensajes de control
    print("Finalizo correctamente")

    # Aseguro los datos como numericos
    float_columns = analisis_df.columns.values.tolist()[7:30]
    analisis_df[float_columns] = analisis_df[float_columns].apply(pd.to_numeric, errors='ignore')

    # Guardo el analisis realizado
    if periodo == str(datetime.date.today()):
        pass  # No guardar datos si el día seleccionado es el día actual del sistema
    else:
        # Checking and creating the folder
        if periodo[:4] == "from":
            analisis_df.to_csv('./Data/Analizadas/analisis_' + table + '_' + periodo + '.csv', index=False)
        else:
            folder = periodo[:-3]
            if not os.path.exists('./Data/Analizadas/' + folder):
                os.makedirs('./Data/Analizadas/' + folder)
            # Salvando el analisis
            analisis_df.to_csv('./Data/Analizadas/' + folder + '/analisis_' + table + '_' + periodo + '.csv',
                               index=False)

    return analisis_df


def obtener_item_real(df, columna):
    """
    Función para obtener la resta del día inicial y el día anterior del SQL que contendran
    los datos de los contadores y van aumentando día a día
    Si el día actual es menor que el anterior, es porque se reinicio
    Sí el día actual es mayor porque sigue aumentando, realizar resta
    """
    num_datos = len(df[columna])
    if num_datos >= 2:
        if df[columna].iloc[-1] >= df[columna].iloc[-2]:
            ultima_fila = df[columna].iloc[-1]
            penultima_fila = df[columna].iloc[-2]
            resultado_resta = ultima_fila - penultima_fila
            return resultado_resta

        elif df[columna].iloc[-1] <= df[columna].iloc[-2]:
            ultima_fila = ultima_fila = df[columna].iloc[-1]
            return ultima_fila

    elif num_datos == 1:
        ultima_fila = df[columna].iloc[-1]
        return ultima_fila
    else:
        raise ValueError("No se puede visualizar el día actual, porque no contiene información.")


def obtener_minutos(valor):
    """
        Función para pasar horas a minutos
    """
    return valor * 60


def analis_eoo_tanques(df):
    """
        Función para realizar operaciones del EOO y de los 6 items definidos en Tanques
        Retorno 2 tablas con el EOO y los 6 items
    """

    # Restar los datos del SQL con los datos del día inicial - el anterior
    Averias_Tanques = obtener_item_real(df, "Averias_Tanques")
    Mtto_programado_Tanques = obtener_item_real(df, "Mtto_programado_Tanques")
    Lavado_moldes_Tanques = obtener_item_real(df, "Lavado_moldes_Tanques")
    Paro_proceso_Tanques = obtener_item_real(df, "Paro_proceso_Tanques")
    Maq_NoProgramada_Tanques = obtener_item_real(df, "Maq_NoProgramada_Tanques")
    Servicios_Tanques = obtener_item_real(df, "Servicios_Tanques")

    # Paso de hora a minutos de todos los datos del df en la columna horas_programadas_tanques
    df['horas_programadas_tanques'] = df['horas_programadas_tanques'].apply(obtener_minutos)
    # Sumo todos los datos del df si son varios días
    minutos_programados = df['horas_programadas_tanques'].sum()
    moldes_tanques = df['moldes_tanques'].sum()
    cavidades_tanques = df['cavidades_tanques'].sum()
    ciclo_ideal_tanques = df['ciclo_ideal_tanques'].sum()
    calidad_tanques = df['calidad_tanques'].sum() / df.shape[0]
    piezas_fabricadas_tanques = df['piezas_fabricadas_tanques'].sum()

    # ----------------------------------------------------------------------------------------------------
    # Operaciones de disponibilidad + OEE
    disponibilidad_intrinsica = ((minutos_programados - Averias_Tanques) / minutos_programados) * 100
    disponibilidad_alzanzada = ((minutos_programados - Averias_Tanques - Mtto_programado_Tanques) /
                                minutos_programados) * 100

    d_operativa_generalizada = ((minutos_programados - Averias_Tanques - Mtto_programado_Tanques -
                                 Lavado_moldes_Tanques - Paro_proceso_Tanques - Maq_NoProgramada_Tanques
                                 - Servicios_Tanques) / minutos_programados) * 100

    piezas_a_realizar = ((d_operativa_generalizada / 100) * minutos_programados / ciclo_ideal_tanques) \
                        * moldes_tanques + cavidades_tanques
    piezas_a_realizar = piezas_a_realizar.sum()

    rendimiento = (piezas_fabricadas_tanques / piezas_a_realizar) * 100

    oee = (d_operativa_generalizada / 100) * (rendimiento / 100) * calidad_tanques * 100

    # ----------------------------------------------------------------------------------------------------
    # Operaciones para cada item y cuantas se dejan de hacer por item
    averias = Averias_Tanques / minutos_programados
    dejan_averias = Averias_Tanques / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    mtt_prog = Mtto_programado_Tanques / minutos_programados
    dejan_mtt_prog = Mtto_programado_Tanques / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    lvd_moldes = Lavado_moldes_Tanques / minutos_programados
    dejan_lvd_moldes = Lavado_moldes_Tanques / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    paro_proceso = Paro_proceso_Tanques / minutos_programados
    dejan_paro_proceso = Paro_proceso_Tanques / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    maq_no_prog = Maq_NoProgramada_Tanques / minutos_programados
    dejan_maq_no_prog = Maq_NoProgramada_Tanques / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    servicios = Servicios_Tanques / minutos_programados
    dejan_servicios = Servicios_Tanques / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    # ----------------------------------------------------------------------------------------------------
    # Tabla para df Disponibilidad
    df_disponibilidad = {"Fecha": df.fecha,
                         'Disponibilidad_Intrinsica [%]': round(disponibilidad_intrinsica, 2),
                         "Disponibilidad_alcanzada [%]": round(disponibilidad_alzanzada, 2),
                         "Disponibilidad_Operativa_Generalizada [%]": round(d_operativa_generalizada, 2),
                         "Piezas_Posibles_Fabricar ": round(piezas_a_realizar, 0),
                         "rendimiento [%]": round(rendimiento, 2),
                         "OEE [%]": round(oee, 2)
                         }
    # ----------------------------------------------------------------------------------------------------
    # Tabla para los 6 items
    df_items = {'Fecha': df['fecha'],
                'Tiempo_Averias': round(averias * 100, 1),
                "dejan_de_hacer_averias": round(dejan_averias * 100, 1),

                'Mtto_programado': round(mtt_prog * 100, 1),
                "dejan_de_hacer_mtto": round(dejan_mtt_prog * 100, 1),

                'Lavado_moldes': round(lvd_moldes * 100, 1),
                "dejan_de_hacer_lvd": round(dejan_lvd_moldes * 100, 1),

                'Paro_procesos': round(paro_proceso * 100, 1),
                "dejan_de_hacer_proceso": round(dejan_paro_proceso * 100, 1),

                'Maq_NoProgramada': round(maq_no_prog * 100, 1),
                "dejan_de_hacer_maq": round(dejan_maq_no_prog * 100, 1),

                'Servicios': round(servicios * 100, 1),
                "dejan_de_hacer_servicios": round(dejan_servicios * 100, 1),
                }
    # ----------------------------------------------------------------------------------------------------
    # Guardo los arreglos en un DataFrame
    df_disponibilidad = pd.DataFrame(df_disponibilidad)
    df_items = pd.DataFrame(df_items)

    return df_disponibilidad, df_items


def analis_eoo_tapas(df):
    """
        Función para realizar operaciones del EOO y de los 6 items definidos en Tapas
        Retorno 2 tablas con el EOO y los 6 items
    """
    # Restar los datos del SQL con los datos del día inicial - el anterior
    Averias_Tapas = obtener_item_real(df, "Averias_Tapas")
    Mtto_programado_Tapas = obtener_item_real(df, "Mtto_programado_Tapas")
    Lavado_moldes_Tapas = obtener_item_real(df, "Lavado_moldes_Tapas")
    Paro_proceso_Tapas = obtener_item_real(df, "Paro_proceso_Tapas")
    Maq_NoProgramada_Tapas = obtener_item_real(df, "Maq_NoProgramada_Tapas")
    Servicios_Tapas = obtener_item_real(df, "Servicios_Tapas")

    # Paso de hora a minutos de todos los datos del df en la columna horas_programadas_tapas
    df['horas_programadas_tapas'] = df['horas_programadas_tapas'].apply(obtener_minutos)
    # Obtengo los datos del Excel y los sumo todos por la cantidad de datos del df
    minutos_programados = df['horas_programadas_tapas'].sum()
    moldes_tanques = df['moldes_tapas'].sum()
    cavidades_tanques = df['cavidades_tapas'].sum()
    ciclo_ideal_tanques = df['ciclo_ideal_tapas'].sum()
    calidad_tanques = df['calidad_tapas'].sum() / df.shape[0]
    piezas_fabricadas_tanques = df['piezas_fabricadas_tapas'].sum()

    # ----------------------------------------------------------------------------------------------------
    # Operaciones de disponibilidad + OEE
    disponibilidad_intrinsica = ((minutos_programados - Averias_Tapas) / minutos_programados) * 100

    disponibilidad_alzanzada = ((minutos_programados - Averias_Tapas - Mtto_programado_Tapas) /
                                minutos_programados) * 100

    d_operativa_generalizada = ((minutos_programados - Averias_Tapas - Mtto_programado_Tapas -
                                 Lavado_moldes_Tapas - Paro_proceso_Tapas - Maq_NoProgramada_Tapas
                                 - Servicios_Tapas) / minutos_programados) * 100

    piezas_a_realizar = ((d_operativa_generalizada / 100) * minutos_programados / ciclo_ideal_tanques) \
                        * moldes_tanques + cavidades_tanques

    rendimiento = (piezas_fabricadas_tanques / piezas_a_realizar) * 100

    oee = (d_operativa_generalizada / 100) * (rendimiento / 100) * calidad_tanques * 100
    # ----------------------------------------------------------------------------------------------------
    # Operaciones para cada item y cuantas se dejan de hacer por item
    averias = Averias_Tapas / minutos_programados
    dejan_averias = Averias_Tapas / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    mtt_prog = Mtto_programado_Tapas / minutos_programados
    dejan_mtt_prog = Mtto_programado_Tapas / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    lvd_moldes = Lavado_moldes_Tapas / minutos_programados
    dejan_lvd_moldes = Lavado_moldes_Tapas / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    paro_proceso = Paro_proceso_Tapas / minutos_programados
    dejan_paro_proceso = Paro_proceso_Tapas / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    maq_no_prog = Maq_NoProgramada_Tapas / minutos_programados
    dejan_maq_no_prog = Maq_NoProgramada_Tapas / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    servicios = Servicios_Tapas / minutos_programados
    dejan_servicios = Servicios_Tapas / (ciclo_ideal_tanques * moldes_tanques * cavidades_tanques)

    # ----------------------------------------------------------------------------------------------------
    # Tabla para df Disponibilidad
    df_disponibilidad = {"Fecha": df['fecha'],
                         'Disponibilidad_Intrinsica [%]': round(disponibilidad_intrinsica, 2),
                         "Disponibilidad_alcanzada [%]": round(disponibilidad_alzanzada, 2),
                         "Disponibilidad_Operativa_Generalizada [%]": round(d_operativa_generalizada, 2),
                         "Piezas_Posibles_Fabricar [%]": round(piezas_a_realizar, 0),
                         "rendimiento [%]": round(rendimiento, 2),
                         "OEE [%]": round(oee, 2)
                         }
    # ----------------------------------------------------------------------------------------------------
    # Tabla para los 6 items
    df_items = {"Fecha": df['fecha'],
                'Tiempo_Averias': round(averias * 100, 1),
                "dejan_de_hacer_averias": round(dejan_averias * 100, 1),

                'Mtto_programado': round(mtt_prog * 100, 1),
                "dejan_de_hacer_mtto": round(dejan_mtt_prog * 100, 1),

                'Lavado_moldes': round(lvd_moldes * 100, 1),
                "dejan_de_hacer_lvd": round(dejan_lvd_moldes * 100, 1),

                'Paro_procesos': round(paro_proceso * 100, 1),
                "dejan_de_hacer_paro_proceso": round(dejan_paro_proceso * 100, 1),

                'Maq_NoProgramada': round(maq_no_prog * 100, 1),
                "dejan_de_hacer_maq": round(dejan_maq_no_prog * 100, 1),

                'Servicios': round(servicios * 100, 1),
                "dejan_de_hacer_servicios": round(dejan_servicios * 100, 1),

                }
    # ----------------------------------------------------------------------------------------------------
    # Guardo los arreglos en un DataFrame
    df_disponibilidad = pd.DataFrame(df_disponibilidad)
    df_items = pd.DataFrame(df_items)

    return df_disponibilidad, df_items
