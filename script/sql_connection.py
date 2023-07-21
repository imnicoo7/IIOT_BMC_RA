# sql connection tools
# ----------------------------------------------------------------------------------------------------------------------
# Library
# ----------------------------------------------------------------------------------------------------------------------
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL

# ----------------------------------------------------------------------------------------------------------------------
# Variables definition
# ----------------------------------------------------------------------------------------------------------------------
load_dotenv('..env')

server = os.environ.get("SERVER")
database = os.environ.get("DATABASE")
table = os.environ.get("TABLE")
disponibilidad = os.environ.get("TABLE2")
username = os.environ.get("USER_SQL")
password = os.environ.get("PASSWORD")

# ----------------------------------------------------------------------------------------------------------------------
# SQL connection definition
# ----------------------------------------------------------------------------------------------------------------------
# Connecting to the sql database
connection_str = "DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % (server, database, username, password)
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_str})

conn = create_engine(connection_url)

# ----------------------------------------------------------------------------------------------------------------------
# SQL execute
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Drop a column
# conn.execute(sa_text('''ALTER TABLE %s DROP COLUMN prueba_texto''' % table).execution_options(autocommit=True))

# ----------------------------------------------------------------------------------------------------------------------
# Modify a column
# conn.execute(sa_text('''ALTER TABLE %s ALTER COLUMN SP_Presion_Agua REAL''' % table).execution_options(autocommit=True))

# ----------------------------------------------------------------------------------------------------------------------
# Adding a column
# conn.execute(sa_text('''ALTER TABLE %s ADD id_averia UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID()''' % table).execution_options(autocommit=True))
# conn.execute(sa_text('''ALTER TABLE %s ADD Valv_Presion_agua REAL ''' % table).execution_options(autocommit=True))

# ----------------------------------------------------------------------------------------------------------------------
# Update a row
# conn.execute(sa_text('''UPDATE %s SET ciclo_cerrado = 1 WHERE id = '69794F53-0560-4BFD-92C6-C29E1374EDC7' ''' % table).execution_options(autocommit=True))

# ----------------------------------------------------------------------------------------------------------------------
# Inspect table
inspector = inspect(conn)

for table_name in inspector.get_table_names():
    print(table_name)
    for column in inspector.get_columns(table_name):
        print(f"Column: {column['name']}, Type: {column['type']}")

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------
#df.to_sql(table, conn, if_exists='append', index=False)

# Read SQL
day = '2023-07-18'
pd_sql = pd.read_sql_query("SELECT * FROM " + database + ".dbo.Disponibilidad" + " WHERE fecha like '" + day + "'", conn)
# pd_sql = pd.read_sql_query("SELECT * FROM " + database + ".dbo." + table, conn)

# pd_sql.to_csv('test.csv', index=False)
pd_sql.to_excel('Climati_salon3_CBC.xlsx', index=False)

