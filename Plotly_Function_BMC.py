# Aplicación de BMC para RA con Python Streamlit
# Plot Function for Ramos Arizpe en México
# 30-MARZO-2023
# ----------------------------------------------------------------------------------------------------------------------
# Libraries
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ----------------------------------------------------------------------------------------------------------------------
# Function definition
def plot_on_off(fig, df, column, legend, rgb, visibility="legendonly", second_y=True,  axis_y="y2", r=1, c=1):

    fig.add_trace(go.Scatter(x=df.index, y=df[column],
                             fill='tozeroy', mode="lines",
                             fillcolor=rgb,
                             line_color='rgba(0,0,0,0)',
                             legendgroup=legend,
                             showlegend=True,
                             name=legend,
                             yaxis=axis_y,
                             visible=visibility)
                  , secondary_y=second_y, row=r, col=c)

    return fig


# @st.cache_data(persist=False, experimental_allow_widgets=True, show_spinner=True, ttl=24 * 3600)
@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True, ttl=24 * 3600)
def plot_html_bmc_tanques(df, title):
    """
    Función para dibujar los datos de BMC RA
        df = pandas dataframe traído de la base de dato SQL
        title = Título de la gráfica
    OUTPUT:
        fig = objeto figura para dibujarlo externamente de la función
    """
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1,  specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
                        shared_xaxes=True, vertical_spacing=0.05)
    # Estado
    fig.add_trace(go.Scatter(x=df.index, y=df["Estado_Tanques"],
                             line=dict(color='black', width=1),
                             mode='lines',  # 'lines+markers'
                             name='Estado Tanques',
                             yaxis="y1",
                             ),
                  row=1, col=1)

    # Presion llenado tanques
    fig.add_trace(go.Scatter(x=df.index, y=df["PrespastaTQ"],
                             line=dict(color='orangered', width=1.5),
                             mode='lines',  # 'lines+markers'
                             name='Presión llenado',
                             yaxis="y3",
                             ),
                  row=2, col=1)
    # Presion prensado tanques
    fig.add_trace(go.Scatter(x=df.index, y=df["PresprensadoTQ"],
                             line=dict(color='#45CEA2', width=1.5),
                             mode='lines',  # 'lines+markers'
                             name='Presión prensado',
                             yaxis="y3",
                             ),
                  row=2, col=1)
    # Temperatura pasta tanques
    fig.add_trace(go.Scatter(x=df.index, y=df["TempPasta"],
                             line=dict(color='#FFC947', width=1, dash='dot'),
                             mode='lines',  # 'lines+markers'
                             name='Temp Pasta',
                             yaxis="y3",
                             ),
                  secondary_y=True, row=2, col=1)
    # Temperatura agua tanques
    fig.add_trace(go.Scatter(x=df.index, y=df["TempAgua"],
                             line=dict(color='#0077be', width=1, dash='dot'),
                             mode='lines',  # 'lines+markers'
                             name='Temp Agua',
                             yaxis="y3"
                             ),
                  secondary_y=True, row=2, col=1)
    # Presión de Linea
    fig.add_trace(go.Scatter(x=df.index, y=df["PresLineaBar"],
                             line=dict(color='gray', width=1.5),
                             mode='lines',  # 'lines+markers'
                             name='Presión de Linea',
                             yaxis="y3",
                             ),
                  row=2, col=1)
    # ---------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    # Add figure title
    fig.update_layout(height=600, width=400, title=title)
    # Template
    fig.layout.template = 'seaborn'  # ggplot2, plotly_dark, seaborn, plotly, plotly_white
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])
    # Set x-axis and y-axis title
    fig.update_layout(legend_title_text='Variables BMC Tanques')
    
    # Setting the x,y-axis of the title and range
    fig['layout']['yaxis']['title'] = 'Presión [Bar]'
    # fig['layout']['yaxis']['range'] = [0, 10]
    fig['layout']['xaxis']['title'] = 'Fecha'
    
    # Setting the y2-axis of the title and range
    fig['layout']['yaxis2']['title'] = 'Temperatura [°C]'
    fig['layout']['yaxis2']['range'] = [0, 80]
    
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

    return fig


# @st.cache_data(persist=False, experimental_allow_widgets=True, show_spinner=True, ttl=24 * 3600)
@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True, ttl=24 * 3600)
def plot_html_bmc_tapas(df, title):
    """
    Función para dibujar los datos de BMC RA
    INPUT:
        df = pandas dataframe traído de la base de dato SQL
        title = Título de la gráfica
    OUTPUT:
        fig = objeto figura para dibujarlo externamente de la función
    """
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, specs=[[{"secondary_y": True}], [{"secondary_y": True}]],
                        shared_xaxes=True, vertical_spacing=0.05)
    # Estado
    fig.add_trace(go.Scatter(x=df.index, y=df["Estado_Tapas"],
                             line=dict(color='black', width=1),
                             mode='lines',  # 'lines+markers'
                             name='Estado Tapas',
                             yaxis="y1",
                             ),
                  row=1, col=1)

    # Presion llenado tapas
    fig.add_trace(go.Scatter(x=df.index, y=df["PrespastaTP"],
                             line=dict(color='orangered', width=1.5),
                             mode='lines',  # 'lines+markers'
                             name='Presión llenado',
                             yaxis="y3",
                             ),
                  row=2, col=1)
    # Presion prensado tapas
    fig.add_trace(go.Scatter(x=df.index, y=df["PresprensadoTP"],
                             line=dict(color='#45CEA2', width=1.5),
                             mode='lines',  # 'lines+markers'
                             name='Presión prensado',
                             yaxis="y3",
                             ),
                  row=2, col=1)
    # Temperatura pasta tapas
    fig.add_trace(go.Scatter(x=df.index, y=df["TempPasta"],
                             line=dict(color='#FFC947', width=1, dash='dot'),
                             mode='lines',  # 'lines+markers'
                             name='Temp Pasta',
                             yaxis="y4",
                             ),
                  secondary_y=True,
                  row=2, col=1)
    # Temperatura agua tapas
    fig.add_trace(go.Scatter(x=df.index, y=df["TempAgua"],
                             line=dict(color='#0077be', width=1, dash='dot'),
                             mode='lines',  # 'lines+markers'
                             name='Temp Agua',
                             yaxis="y4",
                             ),
                  secondary_y=True,
                  row=2, col=1)
    # Presión de Linea
    fig.add_trace(go.Scatter(x=df.index, y=df["PresLineaBar"],
                             line=dict(color='gray', width=1.5),
                             mode='lines',  # 'lines+markers'
                             name='Presión de Linea',
                             yaxis="y3",
                             ),
                  row=2, col=1)
    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # Add figure title
    fig.update_layout(height=600, width=400, title=title)

    # Template
    fig.layout.template = 'seaborn'  # ggplot2, plotly_dark, seaborn, plotly, plotly_white
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    # Set x-axis and y-axis title
    fig.update_layout(legend_title_text='Variables BMC Tapas')
    
    # Setting the x,y-axis of the title and range
    fig['layout']['yaxis']['title'] = 'Estado'
    fig['layout']['yaxis']['range'] = [0, 1]

    fig['layout']['yaxis3']['title'] = 'Presión [Bar]'
    # fig['layout']['yaxis']['range'] = [0, 10]
    fig['layout']['xaxis']['title'] = 'Fecha'

    # Setting the y2-axis of the title and range
    fig['layout']['yaxis4']['title'] = 'Temperatura [°C]'
    fig['layout']['yaxis4']['range'] = [0, 80]

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

    return fig


# @st.cache_data(persist=False, experimental_allow_widgets=True, show_spinner=True, ttl=24 * 3600)
@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True, ttl=24 * 3600)
def plot_html_pres_linea(df, title):
    """
    Función para dibujar los datos del BMC RA
    INPUT:
        df = pandas dataframe traído de la base de dato SQL
        title = Título de la gráfica
    OUTPUT:
        fig = objeto figura para dibujarlo externamente de la función
    """
    # Create figure with secondary y-axis
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.02)
    
    # Presión de Linea en PSI
    fig.add_trace(go.Scatter(x=df.index, y=df["PresLinea"],
                             line=dict(color='gray', width=1),
                             mode='lines',  # 'lines+markers'
                             name='Presión de Linea',
                             yaxis="y1",
                             showlegend=True
                             ),
                  row=1, col=1)

    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # Add figure title
    fig.update_layout(height=500, width=400, title=title)

    # Template
    fig.layout.template = 'seaborn'  # ggplot2, plotly_dark, seaborn, plotly, plotly_white
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    # Set x-axis and y-axis title
    fig.update_layout(legend_title_text='Variables BMC Tapas')
    
    # Setting the x,y-axis of the title and range
    fig['layout']['yaxis']['title'] = 'Presión [PSI]'
    fig['layout']['yaxis']['range'] = [0, 120]
    fig['layout']['xaxis']['title'] = 'Fecha'

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

    return fig


# @st.cache_data(persist=False, experimental_allow_widgets=True, show_spinner=True, ttl=24 * 3600)
@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True, ttl=24 * 3600)
def plot_html_corrientes(df, title):
    """
        Función para dibujar los datos del BMC RA
        INPUT:
            df = pandas dataframe traído de la base de dato SQL
            title = Título de la gráfica
        OUTPUT:
            fig = objeto figura para dibujarlo externamente de la función
        """
    # Create figure with secondary y-axis
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]], shared_xaxes=True, vertical_spacing=0.05)

    # Elevador delantero tanques [A]
    fig.add_trace(go.Scatter(x=df.index, y=df["elevador_delantero_tanques"],
                             line=dict(color='#CF1111', width=1.5),
                             mode='lines',  # 'lines+markers'
                             name='Delantero TQ',
                             yaxis="y1",
                             ),
                  row=1, col=1)

    # Elevador trasero tanques [A]
    fig.add_trace(go.Scatter(x=df.index, y=df["elevador_trasero_tanques"],
                             line=dict(color='#0006BC', width=1.5),
                             mode='lines',  # 'lines+markers'
                             visible="legendonly",
                             name='Trasero TQ',
                             yaxis="y1",
                             ),
                  row=1, col=1)

    # Elevador delantero tapas [A]
    fig.add_trace(go.Scatter(x=df.index, y=df["elevador_delantero_tapas"],
                             line=dict(color='#ff9900', width=1.5),
                             mode='lines',  # 'lines+markers'
                             visible="legendonly",
                             name='Delantero TP',
                             yaxis="y1",
                             ),
                  row=1, col=1)

    # Elevador trasero tapas [A]
    fig.add_trace(go.Scatter(x=df.index, y=df["elevador_trasero_tapas"],
                             line=dict(color='#006710', width=1.5),
                             mode='lines',  # 'lines+markers'
                             visible="legendonly",
                             name='Trasero TP',
                             yaxis="y1",
                             ),
                  row=1, col=1)

    # TQ ELV DL MOV
    fig = plot_on_off(fig, df, "TQ_ELV_DL", "MOV DL TQ", 'rgba(207,17,17,0.3)', visibility=None)
    # TQ ELV TR MOV
    fig = plot_on_off(fig, df, "TQ_ELV_TR", "MOV TR TQ", 'rgba(0,6,188,0.3)', visibility="legendonly")
    # TP ELV DL MOV
    fig = plot_on_off(fig, df, "TP_ELV_DL", "MOV DL TP", 'rgba(255,153,0,0.3)', visibility="legendonly")
    # TP ELV TR MOV
    fig = plot_on_off(fig, df, "TP_ELV_TR", "MOV TR TP", 'rgba(0,103,16,0.3)', visibility="legendonly")

    # -----------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------
    # Add figure title
    fig.update_layout(height=450, width=400, title=title)
    # Template
    fig.layout.template = 'seaborn'  # ggplot2, plotly_dark, seaborn, plotly, plotly_white
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])
    # Set x-axis and y-axis title
    fig.update_layout(legend_title_text='Variables BMC Corrientes Elevadores')

    # Setting the x,y-axis of the title and range
    fig['layout']['yaxis']['title'] = 'Corriente Elevador [A]'
    fig['layout']['yaxis']['range'] = [0, 12.5]
    fig['layout']['xaxis']['title'] = 'Fecha'
    fig['layout']['yaxis2']['range'] = [0.9, 3]
    fig['layout']['yaxis2']['title'] = 'Movimiento de elevadores'

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

    return fig


# @st.cache_data(persist=False, experimental_allow_widgets=True, show_spinner=True, ttl=24 * 3600)
@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True, ttl=24 * 3600)
def plot_tiempo_muerto(df, title_plot):
    """
    Función para dibujar los tiempos de espera de los ciclos 1 misma gráfica
    INPUT:
        df = Pandas dataframe que tiene los tiempos de espera
        title = Título de la gráfica
    OUTPUT:
        fig = Objeto figura para dibujarlo externamente de la función
    """

    fig = go.Figure()
    
    # Tiempo espera
    fig.add_trace(go.Scatter(x=df["Hora"], y=df["Tiempo_Espera [m]"],
                             line=dict(width=2, shape='hv'),
                             mode='lines',  # 'lines+markers'
                             name='Tiempo_Ciclo', showlegend=True))

    # Add figure title
    fig.update_layout(height=500, width=700, template="seaborn", title=title_plot)
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    # Set x-axis and y-axis title
    fig['layout']['xaxis']['title'] = 'Fecha'
    fig['layout']['yaxis']['title'] = 'Tiempo espera [M]'
    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    return fig


# @st.cache_data(persist=False, experimental_allow_widgets=True, show_spinner=True, ttl=24 * 3600)
@st.cache(persist=False, allow_output_mutation=True, suppress_st_warning=True, show_spinner=True, ttl=24 * 3600)
def plot_bar_acum_tiempo_muerto(df_raw, title_plot):
    """
    Función para en barra el acumulado de los tiempos de espera de los ciclos 1 misma gráfica
    INPUT:
        df = Pandas dataframe que tiene el groupby sum de los tiempos de espera
        title = Título de la gráfica
    OUTPUT:
        fig = Objeto figura para dibujarlo externamente de la función
    """
    # Plotly
    fig = go.Figure()

    # Sumo y convierto a minutos
    df = df_raw.groupby(by="Fecha").sum(numeric_only=True)

    df.reset_index(inplace=True)

    # Bar plot together
    fig.add_trace(go.Bar(x=df['Fecha'],
                         y=df['Tiempo_Espera [m]'],
                         name="Total tiempo espera"))

    fig.update_layout(barmode='group', xaxis_tickangle=0) #  bargap=0.3, bargroupgap=0.02
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")

    # Add figure title
    fig.update_layout(height=500, width=700, template="seaborn", title=title_plot)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0.01))

    # Set x-axis and y-axis title
    fig['layout']['xaxis']['title'] = 'Ciclos'
    fig['layout']['yaxis']['title'] = 'Tiempo Espera [Min]'

    fig.update_xaxes(showline=True, linewidth=0.5, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=0.5, linecolor='black')

    return fig
