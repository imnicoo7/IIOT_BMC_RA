# Python File function for streamlit tools
# SQL connection for IIOT | Colceramica
# July-2021
# ----------------------------------------------------------------------------------------------------------------------
# Libraries
import datetime
import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# ----------------------------------------------------------------------------------------------------------------------

# Function definition
def load_data(folder="./data/", filename="BMCRA2023-03-30.csv"):
    """
    Función que carga el archivo csv guardado al conectar con la base de datos y devuelve un
    dataframe
    """
    df = pd.read_csv(folder + filename, )
    return df


def find_load(tipo, day, ini, database, table, redownload):
    """
    Función que busca y carga el archivo de datos si este ya ha sido descargado. En caso contrario
    lo descarga a través de la función sql_connet
    INPUT:
        tipo: ["day_planta", "rango_planta"].
        day: día final o unico día a analizar como STR ("2023-03-30").
        ini: día inicial a analizar en el rango como STR ("2023-12-28").
        database: base de dato a la cual se debe conectar.
        table: tabla a la cual se debe conectar.
        redownload = TRUE or FALSE statement si es TRUE se omite la parte de buscar el archivo y se
        descarga nuevamente.
    OUTPUT:
        pd_sql: dataframe con los datos buscados o descargados
    """
    # Configuracion de la carpeta para buscar
    directory = './Data/Raw/' + day[:-3] + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    filenames = os.listdir(directory)

    # Empty dataframe
    pd_sql = pd.DataFrame()

    if tipo == "day":
        # Creo el nombre del archivo a buscar
        filename = table + '_' + day + '.csv'
        if filename in filenames and redownload is False:
            pd_sql = load_data(folder=directory, filename=filename)
        else:
            pd_sql = sql_connect(tipo, day, database, table)

    elif tipo == 'rango_planta':
        # Fecha Inicial
        l_ini_n = [int(x) for x in ini.split("-")]
        ini_date = datetime.date(l_ini_n[0], l_ini_n[1], l_ini_n[2])
        # Fecha Final
        l_day_n = [int(x) for x in day.split("-")]
        day_date = datetime.date(l_day_n[0], l_day_n[1], l_day_n[2])

        # Recorro los días de ese periodo de tiempo
        while ini_date <= day_date:
            # Setting the folder where to search
            directory = './Data/Raw/' + str(ini_date)[:-3] + '/'
            if not os.path.exists(directory):
                os.makedirs(directory)
            filenames = os.listdir(directory)

            # Creo el nombre del archivo a buscar
            filename = table + '_' + str(ini_date) + '.csv'
            if filename in filenames and redownload is False:
                aux = load_data(folder=directory, filename=filename)
            else:
                aux = sql_connect(tipo="day", day=str(ini_date), database=database, table=table)

            pd_sql = pd.concat([pd_sql, aux])
            # Avanzo un día
            ini_date = ini_date + datetime.timedelta(days=1)

    return pd_sql


def organize_df(df):
    """
    Función que organiza el data frame, generando nuevas columnas de informaciónd e fechas, reorganizando las columnas
    y redodeando los valores a 2 cifras decimales.
    INPUT:
        df = data frame original
        sql_table = Selección de la tabla SQL de climatización a la que se conectara
    OUTPUT:
        df = data frame  reorganizado
    """

    # Organizar fecha
    df["fecha"] = pd.to_datetime(df['fecha'], format='%Y/%m/%d', exact=False)  # format='mixed')
    df['fecha'] += pd.to_timedelta(df["hora"], unit='h')
    df['fecha'] += pd.to_timedelta(df["minuto"], unit='m')
    df['fecha'] += pd.to_timedelta(df["segundo"], unit='s')

    # Separar los años, meses y días
    df["año"] = df["fecha"].dt.year
    df["ndia"] = df["fecha"].dt.day_name()
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day

    # Convertir valores dataframe de PSI A BAR y lo redondea a 1 decimales
    df['PrespastaTQ'] = df['PrespastaTQ'] * 0.0689476
    df['PresprensadoTQ'] = df['PresprensadoTQ'] * 0.0689476
    df['PrespastaTP'] = df['PrespastaTP'] * 0.0689476
    df['PresprensadoTP'] = df['PresprensadoTP'] * 0.0689476
    df['PresLineaBar'] = df['PresLinea'] * 0.0689476

    # Round the complete dataframe
    df = df.round(2)

    # Ordeno la data por la fecha
    df = df.sort_values(by='fecha', ascending=True)
    # Fecha pasa a ser el index
    df.set_index("fecha", inplace=True)

    return df


def add_day(day, add=1):
    """
    Función agrega o quita dias, teniendo en cuenta inicio de mes e inicio de año
    INPUT
        day = "2023-03-01"  EN STRING
    OUTPUT
        ini_date = día entregado en STR
        fin_date = día con los días sumados o restados en STR al día ingresado
    """
    l_day_n = [int(x) for x in day.split("-")]
    ini_date = datetime.date(l_day_n[0], l_day_n[1], l_day_n[2])
    fin_date = ini_date + datetime.timedelta(days=add)

    return str(ini_date), str(fin_date)


def get_data_day(sel_dia="2023-01-01", sql_table="BMC_RA", flag_download=False):
    """
    Programa que permite conectar con una base de dato del servidor y devuelve la base de dato
    como un pandas dataframe
    INPUT:
        sel_dia = Día inicial EN STR
        sql_table = Selección de la tabla SQL de climatización a la que se conectara
        redownload = Debe descargarse la data o buscar dentro de los archivos previamente descargados.
    OUTPUT:
        df = pandas dataframe traído de la base de dato SQL
        salud_list = lista con el dato de salud por día
        salud_datos = Número | Salud total de los datos
        title = Título para la gráfica
    """

    # Conexion a la base de datos
    if sql_table in ['BMC Tanques', 'BMC Tapas', 'Presión de linea', 'Corriente de elevadores']:
        df = find_load(tipo='day', day=str(sel_dia), ini=None, database='BMCRA', table='BMCRA',
                       redownload=flag_download)

    # Organización del df
    df = organize_df(df)
    datos_dias = 24 * 60 * 60
    # 24 horas en un día x 60 minutos en cada hora x 60 veces que tomo el dato cada minuto

    # Defining the title and filename for saving the plots
    title = f"Gráfica de BMC el {sel_dia}"

    # Salud de los datos
    salud_datos = (df.shape[0] / datos_dias) * 100
    salud_list = [np.round(salud_datos, 2)]

    return df, salud_list, salud_datos, title


def sql_connect(tipo="day", day="023-03-30", database='BMCRA', table="BMCRA"):
    """
    Programa que permite conectar con una base de dato del servidor y devuelve la base
    de dato como un pandas dataframe
    INPUT:
        tipo = ["day_planta", "day"]
        day = Día a descargar en  STR ("2021-04-28")
        database: base de dato a la cual se debe conectar
        table: tabla a la cual se debe conectar
    OUTPUT:
        pd_sql = pandas dataframe traído de la base de dato SQL
    """
    # Connection keys
    load_dotenv('../.env')

    server = os.environ.get("SERVER")
    username = os.environ.get("USER_SQL")
    password = os.environ.get("PASSWORD")
    # Connecting to the sql database
    connection_str = f'DRIVER={{SQL SERVER}};SERVER={server};DATABASE={database};\
    UID={username};PWD={password}'
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_str})

    conn = create_engine(connection_url)
    # ---------------------------------------------------------------------------------------------------
    # Tipos de conexiones establecidas para traer distintas cantidades de datos
    # ---------------------------------------------------------------------------------------------------
    if tipo == "day":
        pd_sql = pd.read_sql_query("SELECT * FROM " + database + ".dbo." + table + " WHERE fecha like '"
                                   + day + "'", conn)
        # Guardando los datos en archivos estaticos
        if day == str(datetime.date.today()):
            pass  # No guardar datos si el día seleccionado es el día actual del sistema
        else:
            # Checking and creating the folder
            folder = day[:-3]
            if not os.path.exists('./Data/Raw/' + folder):
                os.makedirs('./Data/Raw/' + folder)
            # Saving the raw data
            pd_sql.to_csv('./Data/Raw/' + folder + '/' + table + '_' + day + '.csv', index=False)

    return pd_sql
