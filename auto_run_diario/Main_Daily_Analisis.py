# Python File for analysing the data
# GUI APP for IIOT | Corona
# July-2022
# ----------------------------------------------------------------------------------------------------------------------
# Libraries
import datetime

from SQL_Function_Daily import get_data_day
from Analysis_Function_Daily import find_analisis

# ----------------------------------------------------------------------------------------------------------------------
# Setting the condition for the analisis
ayer = datetime.date.today() - datetime.timedelta(days=1)
flag_download = True

# ----------------------------------------------------------------------------------------------------------------------
# Getting the data
print("Se descargara el día {} de BMC Tanques".format(ayer))
df, salud_list, salud_datos, title = get_data_day(ayer, "BMC Tanques", flag_download)
text_dia = str(ayer)

print("Se analizara el día {} de BMC Tanques".format(ayer))
Analisis_df_raw = find_analisis(df=df, sel_bmc="BMC Tanques", text_dia=text_dia, redownload=flag_download)

# ----------------------------------------------------------------------------------------------------------------------
# Getting the data
print("Se descargara el día {} de BMC Tapas".format(ayer))
df, salud_list, salud_datos, title = get_data_day(ayer, "BMC Tapas", flag_download)
text_dia = str(ayer)

print("Se analizara el día {} de BMC Tapas".format(ayer))
Analisis_df_raw = find_analisis(df=df, sel_bmc="BMC Tapas", text_dia=text_dia, redownload=flag_download)
