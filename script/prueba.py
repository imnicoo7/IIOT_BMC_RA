import pandas as pd
import os
import datetime

<<<<<<< HEAD:prueba.py
sel_dia="2023_03_30"
ejemplo_dir = 'C://Users//nsgutierrez//OneDrive - Corona//Documentos//BMC_RA//IIOT_BMC_RA//data//'
nombre_archivo = f'BMCRA{sel_dia}.csv'
=======
df = pd.read_csv('../BMCRA2023_3_30.csv') #0.1087782010436058
>>>>>>> ddaa7138b25b3680b078308312f532416b908457:script/prueba.py

ruta_archivo = os.path.join(ejemplo_dir, nombre_archivo)
    # if flag_download:
    #     # Descargar el archivo si se solicita la descarga
    #     # Descarga el archivo desde la fuente y guárdalo en ruta_archivo  
    # else:
    #     # Leer el archivo desde la ruta_archivo especificada
df = pd.read_csv(ruta_archivo)

print(df)

@st.cache_data(persist=False, experimental_allow_widgets=True, show_spinner=True, ttl=24 * 3600)
def plot_html_BMC_Tanques(df, title): 
    
# Función para dibujar los datos de temperatura de los salones CBC-BDT
# INPUT:
# df = pandas dataframe traído de la base de dato SQL
# title = Título de la gráfica
# OUTPUT:
# fig = objeto figura para dibujarlo externamente de la función
# Organizar el tema de fecha
    
    
# Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)
#variables a utilizar
# Presion prensado tanques
    fig.add_trace(go.Scatter(x=df['fecha'], y=df["PresprensadoTQ"],
    line=dict(color='#174BD6', width=1.5), # dash='dash'),
    mode='lines', # 'lines+markers'
    name='Presión Llenado Tanques',
    yaxis="y1",
    ),
    row=1, col=1,)

# presion pasta tanques
    fig.add_trace(go.Scatter(x=df['fecha'], y=df["PrespastaTQ"],
    line=dict(color='#d62728', width=1.5),
    mode='lines', # 'lines+markers'
    name='Presión Prensado Tanques',
    yaxis="y1",
    ),
    row=1, col=1)
    
# ------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------
    
    # Add figure title
    fig.update_layout(height=800, title= title)

    # Template
    fig.layout.template = 'plotly_dark' # ggplot2, plotly_dark, seaborn, plotly, plotly_white
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    # Set x-axis and y-axis title
    fig.update_layout(legend_title_text='Variables BMC Ramos Arizpe')
    
    fig['layout']['yaxis']['title'] = 'Presión (Bar)'

    fig['layout']['xaxis']['title'] = 'fecha'
    

    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    return fig
