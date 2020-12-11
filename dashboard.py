import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
import datetime
import psycopg2 as pg2
from functions import *
from dashboard_graphs import *
from dashboards_tables import *
import update_database

pio.templates.default = "plotly_white"
db_name = 'cenace'


conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
cursor = conn.cursor()

cursor.execute("""SELECT DISTINCT(zona_de_carga) FROM consumption_real;""")
zonas_de_carga = [zona[0] for zona in cursor.fetchall()]
zonas_de_carga_alone = zonas_de_carga.copy()
zonas_de_carga.append('MEXICO (PAIS)')

cursor.execute("""SELECT DISTINCT(zona_de_carga) FROM nodes_info;""")
zonas_de_carga_precios = [zona[0] for zona in cursor.fetchall()]

cursor.execute("""SELECT clave_nodo FROM nodes_info WHERE zona_de_carga = 'OAXACA';""")
nodos_oaxaca = [nodo[0] for nodo in cursor.fetchall()]



zones_list = {'sin':get_zones_list(cursor, system='sin', market='mda'),
            'bca':get_zones_list(cursor, system='bca', market='mda'),
            'bcs':get_zones_list(cursor, system='bcs', market='mda')}




style1 = {'font-family': 'Arial', 'font-size': '150%'}
style0 = {'text-align':'center','font-family': 'Arial', 'font-size': '100%', 'width': '50%', 'display': 'inline-block', 'vertical-align': 'middle'}
dropdown_style = {'width': '28%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
dropdown_style_2 = {'width': '90%', 'font-family': 'Arial', 'vertical-align': 'middle'}

app = dash.Dash(__name__, title='Energía de México', update_title='Cargando...', external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div(html.Center(html.Div([
    html.Div(html.P()),
    html.Div([
        html.Div([],
            style = {'width': '20%', 'display': 'inline-block', 'align-items': 'left','vertical-align': 'middle'}
            ),
        html.Div(dcc.Markdown('# **Dashboard de Energía en México**'),
            style = style0
            ),
        html.Div([
            html.Div(dcc.Loading(
                            id="loading_element_update_database",
                            type="circle",
                            children=[
                                dbc.Button("Actualizar BD",
                                    id = 'update_database_button',
                                    color="primary",
                                    className="mr-1"
                                    ),
                                ]
                            ),
                style = {'marginBottom': 1, 'float':'right'}
                ),
            html.Div(dcc.Loading(
                id="loading_element_SQL_reconnect_button",
                type="circle",
                children=[
                    dbc.Button("Conectar de nuevo con SQL",
                        id = 'SQL_reconnect_button',
                        color="warning",
                        className="mr-1"
                        )
                    ]
                ),
                style = {'marginBottom': 1, 'float':'right'}
                )
            ],
            style = {'width': '20%','align-items': 'right', 'display':'inline-block', 'vertical-align': 'middle'}
            )
        ],
        style = {'vertical-align': 'middle'}
        ),
    html.Div(html.P()),
    dcc.Tabs([
        dcc.Tab(label='Generación y Demanda',
            style = style1,
            selected_style = style1,
            children=[
                html.Div(
                    dcc.Graph(
                        id = 'daily_generation_graph',
                        figure = generation_daily(cursor)),
                    style = {'width': '50%', 'display': 'inline-block'}
                    ),
                html.Div(
                    dcc.Graph(
                        id = 'hourly_generation_graph',
                        figure = generation_hourly(cursor)),
                    style = {'width': '50%', 'display': 'inline-block'}),
                html.Div(children = [
                    html.Div(
                        dcc.Dropdown(
                            id = 'zona_de_carga_dopdown',
                            options = [{'label': zona, 'value': zona} for zona in zonas_de_carga],
                            multi = True,
                            placeholder = "Selecciona una Zona de Carga",
                            value = ['OAXACA'],
                            style = {'text-align':'center'}),
                        style = {'width': '20%', 'display': 'inline-block','vertical-align': 'top', 'align-items': 'center', 'font-family': 'Arial'},
                        ),
                    html.Div(dcc.Loading(
                            id="loading_element_consumption",
                            type="circle",
                            children=[html.Div(
                                dcc.Graph(
                                    id = 'daily_consumption_graph',
                                    figure = consumption_daily(cursor)
                                    ),
                                )]
                            ),
                        style = {'width': '80%', 'display': 'inline-block'}
                        )
                    ]),
                ]
            ),
        dcc.Tab(label='Precios de Energía',
            style = style1,
            selected_style = style1,
            children=[
                html.Div(html.P()),
                html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                html.Div(
                    dcc.Dropdown(
                        id = 'system_dropdown',
                        options = [
                            {'label': 'Sistema Interconectado Nacional (SIN)', 'value': 'sin'},
                            {'label': 'Sistema Interconectado Baja California (BCA)', 'value': 'bca'},
                            {'label': 'Sistema Interconectado Baja California Sur (BCS)', 'value': 'bcs'}],
                        placeholder = "Selecciona un sistema",
                        value = 'sin',
                        clearable=False,
                        style = {'text-align':'center'}),
                    style = dropdown_style
                    ),
                html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                html.Div(
                    dcc.Dropdown(
                        id = 'market_dropdown',
                        options = [
                            {'label': 'Mercado del Día en Adelanto (MDA)', 'value': 'mda'},
                            {'label': 'Mercado de Tiempo Real (MTR)', 'value': 'mtr'}],
                        placeholder = "Selecciona un tipo de mercado",
                        value = 'mda',
                        clearable=False,
                        style = {'text-align':'center'}),
                    style = dropdown_style
                    ),
                html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                html.Div(
                    dcc.Dropdown(
                        id = 'zona_de_carga_prices_dopdown',
                        options = [{'label': zona, 'value': zona} for zona in zones_list['sin']],
                        placeholder = "Selecciona una Zona de Carga",
                        value = 'OAXACA',
                        clearable=False,
                        style = {'text-align':'center'}),
                    style = dropdown_style
                    ),
                html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                html.Div(html.P()),
                html.Div(
                    dcc.Graph(
                        id = 'zone_daily_price_graph',
                        figure = zone_daily_prices(cursor, 'sin','mda','OAXACA')),
                    style = {'width': '50%', 'display': 'inline-block'}
                    ),
                html.Div(
                    dcc.Graph(
                        id = 'zone_hourly_price_graph',
                        figure = zone_hourly_prices(cursor)),
                    style = {'width': '50%', 'display': 'inline-block'}),
                html.P([]),
                html.Div(
                    children=[
                        # html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                        html.Div(
                            dcc.Dropdown(
                                id = 'price_graph_comparisson_dropdown',
                                options = [
                                    {'label': 'OAXACA vs Nodos Locales', 'value': 'nodos'},
                                    {'label': 'OAXACA vs Zonas de Carga', 'value': 'zonas'}],
                                multi = False,
                                value = 'nodos',
                                clearable=False,
                                style = {'text-align':'center'}),
                            style = dropdown_style_2
                            ),
                        html.Div(html.P()),
                        # html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                        html.Div(
                            dcc.Dropdown(
                                id = 'price_component_dropdown',
                                options = [
                                    {'label': 'Precio Total de Energía', 'value': 'precio_e'},
                                    {'label': 'Componente de Energía', 'value': 'c_energia'},
                                    {'label': 'Componente de Pérdidas', 'value': 'c_perdidas'},
                                    {'label': 'Componente de Congestión', 'value': 'c_congestion'}],
                                multi = False,
                                value = 'precio_e',
                                clearable=False,
                                style = {'text-align':'center'}),
                            style = dropdown_style_2
                            ),
                        html.Div(html.P()),
                        # html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                        html.Div(
                            dcc.Dropdown(
                                id = 'price_component_graph_type_dropdown',
                                options = [
                                    {'label': 'Valor Real', 'value': 'real'},
                                    {'label': 'Diferencia vs Zona de Carga', 'value': 'percent'}],
                                multi = False,
                                value = 'real',
                                clearable=False,
                                style = {'text-align':'center'}),
                            style = dropdown_style_2
                            ),
                        html.Div(html.P()),
                        # html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                        html.Div(
                            dcc.Dropdown(
                                id = 'zona_de_carga_prices_comparison_dopdown',
                                options = [{'label': zona, 'value': zona} for zona in zones_list['sin']],
                                multi = True,
                                placeholder = "Selecciona una Zona de Carga",
                                style = {'text-align':'center'}),
                            style = dropdown_style_2
                            ),
                        html.Div(html.P()),
                        html.Div(
                            dbc.Button(
                                id = 'show_table_prices',
                                children = "Obtener más información",
                                color="primary",
                                className="mr-1"),
                            style = dropdown_style_2
                            )
                        ],
                    style = {'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}
                    ),
                html.Div(
                    dcc.Loading(
                            id="loading_element_prices",
                            type="circle",
                            children=[html.Div(
                                dcc.Graph(
                                    id = 'marginal_zones_prices_graph',
                                    figure = marginal_prices(cursor)
                                    )
                            )]
                        ),
                    style = {'width': '70%', 'display': 'inline-block'}
                    ),
                html.Div(html.P()),
                html.H3([f"Información de {datetime.datetime.now().year}"], id = 'prices_table_header'),
                dcc.Loading(
                    id = 'loading_element_table_prices',
                    type = 'circle',
                    children = [
                        html.Div(
                            id = 'prices_table_div',
                            children = [' \n ']
                            )
                        ]
                    ),
                html.Div(html.P()),
                dcc.Loading(
                    id = 'loading_element_download_table_prices',
                    children =[
                        dbc.Button("Descargar",id = 'download_table_prices_button', color="primary", className="mr-1"),
                        ]
                    ),
                html.Div(html.P())
                ]
            ),
        dcc.Tab(label='Localización de Nodos',
            style = style1,
            selected_style = style1,
            children=[
                html.Div(html.P()),
                html.Div(
                    dbc.Input(
                        id="latitud_input",
                        placeholder="Latitud",
                        type="number",
                        debounce = True
                        ),
                    style = {'width': '20%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                    ),
                html.Div([], style = {'width': '2%', 'display': 'inline-block'}),
                html.Div(
                    dbc.Input(
                        id="longitud_input",
                        placeholder="Longitud",
                        type="number",
                        debounce = True
                        ),
                    style = {'width': '20%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                    ),
                html.Div([], style = {'width': '2%', 'display': 'inline-block'}),
                html.Div('Número de nodos a buscar:', style = {'display': 'inline-block'}),
                html.Div([], style = {'width': '0.5%', 'display': 'inline-block'}),
                html.Div(
                    dcc.Dropdown(
                        id = 'number_of_nodes_dropdown',
                        options = [{'label':i, 'value':i} for i in range(1,2001)],
                        value = 5,
                        clearable=False,
                        style = {'text-align':'left'}),
                    style = {'width': '5%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                    ),
                html.Div([], style = {'width': '2%', 'display': 'inline-block'}),
                html.Div(
                    dbc.Button("Buscar",id = 'map_button', color="primary", className="mr-1"),
                    style = {'width': '6%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                    ),
                html.Div([], style = {'width': '5%', 'display': 'inline-block'}),
                html.Div(
                    dcc.Dropdown(
                        id = 'mapbox_style_dropdown',
                        options = [
                            {'label': 'Mapa', 'value': 'open-street-map'},
                            {'label': 'Satélite', 'value':'stamen-terrain'}],
                        value = 'open-street-map',
                        clearable=False,
                        style = {'text-align':'left'}),
                    style = {'width': '10%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                    ),
                html.Div(html.P()),
                dcc.Loading(
                    id="loading_element_map",
                    type="circle",
                    children=[html.Div(
                        dcc.Graph(
                            id = 'map_graph',
                            figure = locate_close_nodes(cursor)
                            ),
                        )]
                    ),
                html.Div(html.P()),
                html.H3([f"Información de nodos seleccionados - {datetime.datetime.now().year}"]),
                dcc.Loading(
                    id = 'loading_element_table_map',
                    type = 'circle',
                    children = [
                        html.Div(
                            id = 'map_table_div',
                            # children = [html.P(),html.P()]
                            ),
                        ]
                    ),
                html.Div(html.P()),
                dcc.Loading(
                    id = 'loading_element_download_table_map',
                    children =[
                        dbc.Button("Descargar",id = 'download_table_map_button', color="primary", className="mr-1"),
                        ]
                    ),
                html.Div(html.P())

                ]
            ),
        dcc.Tab(label='Descarga de Datos',
            style = style1,
            selected_style = style1,
            children=[
                html.P(),
                dcc.Tabs(children = [
                    dcc.Tab(label='Generación',
                        style = style1,
                        selected_style = style1,
                        children=[
                            html.P(),
                            html.P(),
                            html.Div([
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.DatePickerRange(
                                        id='data_generation_date_picker',
                                        min_date_allowed=datetime.date(2018, 1, 1),
                                        max_date_allowed=datetime.datetime.now(),
                                        initial_visible_month=datetime.date(2018, 1, 1),
                                        end_date=datetime.datetime.now()
                                        ),
                                    ],
                                    style = {'width': '20%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle', 'align-items':'left'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div(
                                    dcc.Dropdown(
                                        id = 'data_generation_real_forecast_select_dropdown',
                                        options = [
                                            {'label': 'Generación REAL', 'value': 'real'},
                                            {'label': 'Generación PRONÓSTICO', 'value': 'forecast'}],
                                        value = 'real',
                                        clearable=False,
                                        style = {'text-align':'left'}),
                                    style = {'width': '18%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Loading(
                                        id = 'loading_element_data_generation_preview',
                                        children =[
                                            dbc.Button("Vista Previa",
                                                id = 'data_generation_preview_button',
                                                color="primary",
                                                className="mr-1"
                                                )
                                            ]
                                        )
                                    ],
                                    style = {'width': '10%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Loading(
                                        id = 'loading_element_data_generation_download',
                                        children =[
                                            dbc.Button("Descargar",
                                                id = 'data_generation_download_button',
                                                color="success",
                                                className="mr-1"
                                                )
                                            ]
                                        )
                                    ],
                                    style = {'width': '10%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                ],
                                style = {'align-items':'center'}
                                ),
                            html.Div(html.P()),
                            dcc.Loading(
                                id = 'loading_element_table_data_generation',
                                type = 'circle',
                                children = [
                                    html.Div(
                                        id = 'data_generation_table_div',
                                        children=[]
                                        ),
                                    ]
                                )
                            ]
                        ),
                    dcc.Tab(label='Demanda',
                        style = style1,
                        selected_style = style1,
                        children=[
                            html.P(),
                            html.P(),
                            html.Div([
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.DatePickerRange(
                                        id='data_consumption_date_picker',
                                        min_date_allowed=datetime.date(2018, 1, 1),
                                        max_date_allowed=datetime.datetime.now(),
                                        initial_visible_month=datetime.date(2018, 1, 1),
                                        end_date=datetime.datetime.now()
                                        ),
                                    ],
                                    style = {'width': '20%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle', 'align-items':'left'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div(
                                    dcc.Dropdown(
                                        id = 'data_consumption_real_forecast_select_dropdown',
                                        options = [
                                            {'label': 'Consumo REAL', 'value': 'real'},
                                            {'label': 'Consumo PRONÓSTICO', 'value': 'forecast'}],
                                        value = 'real',
                                        clearable=False,
                                        style = {'text-align':'left'}),
                                    style = {'width': '18%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Loading(
                                        id = 'loading_element_data_consumption_preview',
                                        children =[
                                            dbc.Button("Vista Previa",
                                                id = 'data_consumption_preview_button',
                                                color="primary",
                                                className="mr-1"
                                                )
                                            ]
                                        )
                                    ],
                                    style = {'width': '10%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Loading(
                                        id = 'loading_element_data_consumption_download',
                                        children =[
                                            dbc.Button("Descargar",
                                                id = 'data_consumption_download_button',
                                                color="success",
                                                className="mr-1"
                                                )
                                            ]
                                        )
                                    ],
                                    style = {'width': '10%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                ],
                                style = {'align-items':'center'}
                                ),
                            html.Div(html.P()),
                            html.Div(
                                dcc.Dropdown(
                                    id = 'data_consumption_zona_de_carga_dopdown',
                                    options = [{'label': zona, 'value': zona} for zona in zonas_de_carga],
                                    multi = True,
                                    placeholder = "Selecciona una Zona de Carga, para información de todas selecciona MEXICO (PAIS)",
                                    value = ['MEXICO (PAIS)'],
                                    style = {'text-align':'center'}),
                                style = {'width': '70%','vertical-align': 'top', 'align-items': 'center', 'font-family': 'Arial'},
                                ),
                            html.Div(html.P()),
                            dcc.Loading(
                                id = 'loading_element_table_data_consumption',
                                type = 'circle',
                                children = [
                                    html.Div(
                                        id = 'data_consumption_table_div',
                                        children=[]
                                        ),
                                    ]
                                )
                            ]
                        ),
                    dcc.Tab(label='Precios',
                        style = style1,
                        selected_style = style1,
                        children=[
                            html.P(),
                            html.P(),
                            html.Div([
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.DatePickerRange(
                                        id='data_prices_date_picker',
                                        min_date_allowed=datetime.date(2018, 1, 1),
                                        max_date_allowed=datetime.datetime.now(),
                                        initial_visible_month=datetime.date(2018, 1, 1),
                                        end_date=datetime.datetime.now()
                                        ),
                                    ],
                                    style = {'width': '20%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle', 'align-items':'left'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div(
                                    dcc.Dropdown(
                                        id = 'data_prices_market_select_dropdown',
                                        options = [
                                            {'label': 'Mercado de Tiempo Real (MTR)', 'value': 'mtr'},
                                            {'label': 'Mercado del Día en Adelanto (MDA)', 'value': 'mda'}],
                                        value = 'mtr',
                                        clearable=False,
                                        style = {'text-align':'left'}),
                                    style = {'width': '25%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Loading(
                                        id = 'loading_element_data_prices_preview',
                                        children =[
                                            dbc.Button("Vista Previa",
                                                id = 'data_prices_preview_button',
                                                color="primary",
                                                className="mr-1"
                                                )
                                            ]
                                        )
                                    ],
                                    style = {'width': '10%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Loading(
                                        id = 'loading_element_data_prices_download',
                                        children =[
                                            dbc.Button("Descargar",
                                                id = 'data_prices_download_button',
                                                color="success",
                                                className="mr-1"
                                                )
                                            ]
                                        )
                                    ],
                                    style = {'width': '10%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                ],
                                style = {'align-items':'center'}
                                ),
                            html.Div(html.P()),
                            html.Div([
                                html.Div(
                                    dcc.Dropdown(
                                        id = 'data_prices_zone_or_node_dopdown',
                                        options = [
                                            {'label': 'Descargar precios de Zonas de Carga', 'value': 'zones'},
                                            {'label': 'Descargar precios de Nodos', 'value': 'nodes'}
                                            ],
                                        multi = False,
                                        clearable = False,
                                        value = 'nodes',
                                        style = {'text-align':'center'}
                                        ),
                                    style = {'width': '25%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div(
                                    dcc.Dropdown(
                                        id = 'data_prices_zona_de_carga_dopdown',
                                        options = [{'label': zona, 'value': zona} for zona in zonas_de_carga_precios],
                                        multi = True,
                                        placeholder = "Selecciona una Zona de Carga",
                                        value = ['OAXACA'],
                                        style = {'text-align':'center'}
                                        ),
                                    style = {'width': '33%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div(
                                    dcc.Dropdown(
                                        id = 'data_prices_nodes_dopdown',
                                        options = [{'label': nodo, 'value': nodo} for nodo in nodos_oaxaca],
                                        multi = True,
                                        placeholder = "Selecciona un Nodo",
                                        style = {'text-align':'center'}
                                        ),
                                    style = {'width': '33%', 'display': 'inline-block'}
                                    )

                                ],
                                style = {'width': '100%','vertical-align': 'top', 'align-items': 'center', 'font-family': 'Arial'},
                                ),
                            html.Div(html.P()),
                            dcc.Loading(
                                id = 'loading_element_table_data_prices',
                                type = 'circle',
                                children = [
                                    html.Div(
                                        id = 'data_prices_table_div',
                                        children=[]
                                        ),
                                    ]
                                )
                            ]
                        ),
                    dcc.Tab(label='SQL - Query',
                        style = style1,
                        selected_style = style1,
                        children=[
                            html.P(),
                            html.P(),
                            html.Div([
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dbc.Input(id="SQL_input", placeholder="Escribe una query de SQL...", type="text")
                                    ],
                                    style = {'width': '50%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Loading(
                                        id = 'loading_element_data_SQL_preview',
                                        children =[
                                            dbc.Button("Ejecutar",
                                                id = 'data_SQL_preview_button',
                                                color="success",
                                                className="mr-1"
                                                )
                                            ]
                                        )
                                    ],
                                    style = {'width': '10%', 'display': 'inline-block'}
                                    ),
                                html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                # html.Div([
                                #     dcc.Loading(
                                #         id = 'loading_element_data_SQL_download',
                                #         children =[
                                #             dbc.Button("Descargar",
                                #                 id = 'data_SQL_download_button',
                                #                 color="success",
                                #                 className="mr-1"
                                #                 )
                                #             ]
                                #         )
                                #     ],
                                #     style = {'width': '10%', 'display': 'inline-block'}
                                #     ),
                                # html.Div([], style = {'width': '1%', 'display': 'inline-block'}),
                                ],
                                style = {'align-items':'center'}
                                ),
                            html.Div(html.P()),
                            dcc.Loading(
                                id = 'loading_element_table_data_SQL',
                                type = 'circle',
                                children = [
                                    html.Div(
                                        id = 'data_SQL_table_div',
                                        children=[' ']
                                        ),
                                    ]
                                )
                            ]
                        )
                    ]
                    )
                ]
            )
        ]
        ),
    dcc.ConfirmDialog(
        id='update_database_popup',
        message='Actualizar la base de datos puede tardar unos minutos, ¿Estás seguro?',
        displayed = False
    )
    ],
    style = {'width': '95%'}
    )))

@app.callback(
    Output('SQL_reconnect_button','cildren'),
    Input('SQL_reconnect_button', 'n_clicks'))
def reconnect_sql_function(n_clicks):
    cursor.execute("ROLLBACK")
    conn.commit()
    return 'Conectar de nuevo con SQL'


@app.callback(Output('update_database_popup', 'displayed'),
              Input('update_database_button', 'n_clicks'))
def display_confirm(n_clicks):
    if n_clicks:
        return True

@app.callback(Output('update_database_button','cildren'),
              Input('update_database_popup', 'submit_n_clicks'))
def update_output(submit_n_clicks):
    if submit_n_clicks:
        update_database.main()
        return 'Actualizar BD'

@app.callback(
    Output('daily_consumption_graph', 'figure'),
    Input('zona_de_carga_dopdown','value'))
def daily_consumption_graph_function(value):

    fig = consumption_daily(cursor,value)
    return fig

@app.callback(
    Output('hourly_generation_graph', 'figure'),
    Input('daily_generation_graph', 'clickData'))
def hourly_generation_graph_function(clickData):

    days, date = 10 , []
    if clickData:
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') - datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') + datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        fig = generation_hourly(cursor,date)
    else:
        fig = generation_hourly(cursor)

    return fig

@app.callback(
    Output("zona_de_carga_prices_dopdown", "options"),
    [Input("system_dropdown", "value"),
    State('market_dropdown','value')])
def zone_options_pnd(system, market):

    zone_list = zones_list[system]
    return [{'label': zone, 'value': zone} for zone in zone_list]


@app.callback(
    Output('zone_daily_price_graph', 'figure'),
    [Input('zona_de_carga_prices_dopdown','value'),
    State("system_dropdown", "value"),
    State('market_dropdown','value')])
def daily_zone_prices_graph_function(zone,system, market):

    if not zone:
        return 0
    fig = zone_daily_prices(cursor,system, market, zone)

    return fig

@app.callback(
    Output('zone_hourly_price_graph', 'figure'),[
    Input('zone_daily_price_graph', 'clickData'),
    State("system_dropdown", "value"),
    State('market_dropdown','value'),
    State('zona_de_carga_prices_dopdown','value')])
def hourly_zone_prices_graph_function(clickData, system, market, zone):

    days, date = 10 , []
    if clickData:
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') - datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') + datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        fig = zone_hourly_prices(cursor,system, market, zone, date)
    else:
        fig = zone_hourly_prices(cursor)

    return fig


@app.callback(
    Output('marginal_zones_prices_graph', 'figure'),[
    Input('price_component_graph_type_dropdown','value'),
    Input('price_component_dropdown', 'value'),
    Input('price_graph_comparisson_dropdown','value'),
    Input('zona_de_carga_prices_comparison_dopdown', 'value'),
    State('zona_de_carga_prices_dopdown', 'value'),
    State("system_dropdown", "value"),
    State('market_dropdown','value')])
def marginal_prices_graph_function(graph_type, data, zonas_nodos, zones, zona_de_carga, system, market):
    if zonas_nodos == 'zonas':
        fig = zones_prices(cursor, zones, zona_de_carga, system, market, data)
    elif zonas_nodos == 'nodos':
        fig = marginal_prices(cursor, zona_de_carga, system, market, data, graph_type)
    return fig

@app.callback(
    Output("price_graph_comparisson_dropdown", 'options'),
    Input('zona_de_carga_prices_dopdown','value'))
def update_price_dropdown_options(zona_de_carga):
    options = [
        {'label': f'{zona_de_carga} vs Nodos Locales', 'value': 'nodos'},
        {'label': f'{zona_de_carga} vs Zonas de Carga', 'value': 'zonas'}]
    return options

@app.callback(
    Output("zona_de_carga_prices_comparison_dopdown", "options"),
    [Input("system_dropdown", "value")])
def zone_options_prices_comparisson(system):

    zone_list = zones_list[system]
    return [{'label': zone, 'value': zone} for zone in zone_list]


@app.callback([
    Output('zona_de_carga_prices_comparison_dopdown','disabled'),
    Output('price_component_graph_type_dropdown', 'disabled')],
    Input('price_graph_comparisson_dropdown','value'))
def disable_prices_dropdowns(zonas_nodos):

    if zonas_nodos == 'zonas':
        return False, True
    else:
        return True, False


@app.callback(
    Output('map_graph', 'figure'),[
    Input('map_button','n_clicks')],[
    Input('mapbox_style_dropdown', 'value'),
    State('latitud_input', 'value'),
    State("longitud_input", "value"),
    State('number_of_nodes_dropdown','value')])
def update_map(button, mapbox_style, latitud, longitud, number_of_nodes):
    print(button, mapbox_style, latitud, longitud, number_of_nodes)
    fig = locate_close_nodes(cursor, latitud, longitud, number_of_nodes, mapbox_style)
    return fig

@app.callback(
    Output('map_table_div', 'children'),[
    Input('map_graph', 'clickData')])
def map_clickdata_table_function(clickData):
    # print(clickData)
    # print()

    if clickData['points'][0]['customdata'][:2] != ['-','-']:

        estado = clickData['points'][0]['customdata'][0]
        municipio =clickData['points'][0]['customdata'][1]
        df = map_click_table(cursor, estado, municipio)

    else:
        df = map_click_table(cursor, clickData['points'][0]['customdata'][4])

    # print()
    return dbc.Table.from_dataframe(
                            df,
                            id = 'table_map',
                            striped=True,
                            bordered=True,
                            hover=True)

@app.callback(
    Output('download_table_map_button', 'children'),[
    Input('download_table_map_button', 'n_clicks'),
    State('map_graph','clickData')])
def download_map_table_function(n_clicks, clickData):

    if clickData['points'][0]['customdata'][:2] != ['-','-']:
        estado = clickData['points'][0]['customdata'][0]
        municipio =clickData['points'][0]['customdata'][1]
        df = map_click_table(cursor, estado, municipio)

    else:
        df = map_click_table(cursor, clickData['points'][0]['customdata'][4])

    file_name = get_download_file_name('nodos_de_mapa')
    df.to_csv(f"..\\files\\descargas\\{file_name}", index = False)

    return 'Descargar'


@app.callback(
    Output('prices_table_div', 'children'),[
    Input('show_table_prices', 'n_clicks'),
    State('system_dropdown', 'value'),
    State('market_dropdown', 'value'),
    State('zona_de_carga_prices_dopdown', 'value'),
    State('price_graph_comparisson_dropdown', 'value'),
    State('price_component_dropdown','value'),
    State('zona_de_carga_prices_comparison_dopdown','value')])
def prices_create_table_function(n_clicks, system, market, zone, zonas_nodos, price_component, zones):

    if zonas_nodos == 'zonas':
        df = prices_zones_table(cursor, system, market, zone, zones, price_component)
    elif zonas_nodos == 'nodos':
        df = prices_nodes_table(cursor, system, market, zone, price_component)
    else:
        df = pd.DataFrame()

    return dbc.Table.from_dataframe(
                            df,
                            id = 'table_prices',
                            striped=True,
                            bordered=True,
                            hover=True)

@app.callback(
    Output('download_table_prices_button', 'children'),[
    Input('download_table_prices_button', 'n_clicks'),
    State('system_dropdown', 'value'),
    State('market_dropdown', 'value'),
    State('zona_de_carga_prices_dopdown', 'value'),
    State('price_graph_comparisson_dropdown', 'value'),
    State('price_component_dropdown','value'),
    State('zona_de_carga_prices_comparison_dopdown','value')])
def download_prices_table_function(n_clicks, system, market, zone, zonas_nodos, price_component, zones):

    if zonas_nodos == 'zonas':
        df = prices_zones_table(cursor, system, market, zone, zones, price_component)
    if zonas_nodos == 'nodos':
        df = prices_nodes_table(cursor, system, market, zone, price_component)

    file_name = get_download_file_name('precios_de_energia')
    df.to_csv(f"..\\files\\descargas\\{file_name}", index = False)

    return 'Descargar'


@app.callback(
    Output('prices_table_header', 'children'),[
    Input('download_table_prices_button', 'n_clicks'),
    State('system_dropdown', 'value'),
    State('market_dropdown', 'value'),
    State('zona_de_carga_prices_dopdown', 'value'),
    State('price_graph_comparisson_dropdown', 'value'),
    State('price_component_dropdown','value'),
    State('zona_de_carga_prices_comparison_dopdown','value')])
def update_prices_table_header_function(n_clicks, system, market, zone, zonas_nodos, price_component, zones):

    titulos = {
        'precio_e':'Precio Total  De Energía',
        'c_energia':'Componente de Energía',
        'c_perdidas':'Componente de Pérdidas',
        'c_congestion':'Componente de Congestión',}

    if zonas_nodos == 'zonas':
        return f'Información de Zonas de Carga de {datetime.datetime.now().year} - {system.upper()} - {market.upper()} - {titulos[price_component]}'
    if zonas_nodos == 'nodos':
        return f'Información de {zone} y Precios Marginales de {datetime.datetime.now().year} - {system.upper()} - {market.upper()} - {titulos[price_component]}'

@app.callback(
    Output('data_generation_table_div','children'),[
    Input('data_generation_preview_button','n_clicks'),
    State('data_generation_date_picker', 'start_date'),
    State('data_generation_date_picker', 'end_date'),
    State('data_generation_real_forecast_select_dropdown','value')
    ])
def data_generation_preview_function(n_clicks, start_date, end_date, data):

    df = data_generation_preview(cursor,start_date, end_date, data)

    return dbc.Table.from_dataframe(
                            df,
                            id = 'data_generation_table',
                            striped=True,
                            bordered=True,
                            hover=True)


@app.callback(
    Output('data_generation_download_button','children'),[
    Input('data_generation_download_button','n_clicks'),
    State('data_generation_date_picker', 'start_date'),
    State('data_generation_date_picker', 'end_date'),
    State('data_generation_real_forecast_select_dropdown','value')
    ])
def data_generation_download_function(n_clicks, start_date, end_date, data):

    data_generation_download(cursor,start_date, end_date, data)

    return 'Descargar'


@app.callback(
    Output('data_consumption_table_div','children'),[
    Input('data_consumption_preview_button','n_clicks'),
    State('data_consumption_date_picker', 'start_date'),
    State('data_consumption_date_picker', 'end_date'),
    State('data_consumption_real_forecast_select_dropdown','value'),
    State('data_consumption_zona_de_carga_dopdown','value')
    ])
def data_consumption_preview_function(n_clicks, start_date, end_date, data, zones):

    df = data_consumption_preview(cursor,start_date, end_date, data, zones)

    return dbc.Table.from_dataframe(
                            df,
                            id = 'data_consumption_table',
                            striped=True,
                            bordered=True,
                            hover=True)

@app.callback(
    Output('data_consumption_download_button','children'),[
    Input('data_consumption_download_button','n_clicks'),
    State('data_consumption_date_picker', 'start_date'),
    State('data_consumption_date_picker', 'end_date'),
    State('data_consumption_real_forecast_select_dropdown','value'),
    State('data_consumption_zona_de_carga_dopdown','value')
    ])
def data_consumption_download_function(n_clicks, start_date, end_date, data, zones):

    data_consumption_download(cursor,start_date, end_date, data, zones)

    return 'Descargar'


@app.callback(
    Output('data_prices_table_div','children'),[
    Input('data_prices_preview_button','n_clicks'),
    State('data_prices_date_picker','start_date'),
    State('data_prices_date_picker','end_date'),
    State('data_prices_market_select_dropdown', 'value'),
    State('data_prices_zone_or_node_dopdown','value'),
    State('data_prices_zona_de_carga_dopdown','value'),
    State('data_prices_nodes_dopdown','value')
    ])
def data_prices_preview_function(n_clicks, start_date, end_date, market, zonas_nodos, zones, nodes):

    df = data_prices_preview(cursor,start_date, end_date, market, zonas_nodos, zones, nodes)

    return dbc.Table.from_dataframe(
                            df,
                            id = 'data_prices_table',
                            striped=True,
                            bordered=True,
                            hover=True)


@app.callback(
    Output('data_prices_download_button','children'),[
    Input('data_prices_download_button','n_clicks'),
    State('data_prices_date_picker','start_date'),
    State('data_prices_date_picker','end_date'),
    State('data_prices_market_select_dropdown', 'value'),
    State('data_prices_zone_or_node_dopdown','value'),
    State('data_prices_zona_de_carga_dopdown','value'),
    State('data_prices_nodes_dopdown','value')
    ])
def data_prices_download_function(n_clicks, start_date, end_date, market, zonas_nodos, zones, nodes):

    data_prices_download(cursor,start_date, end_date, market, zonas_nodos, zones, nodes)

    return 'Descargar'

@app.callback(
    Output('data_SQL_table_div','children'),[
    Input('data_SQL_preview_button','n_clicks'),
    State('SQL_input','value')
    ])
def data_SQL_preview_function(n_clicks, query_string):

    if n_clicks:
        try:
            df = data_SQL_preview(cursor, query_string)
        except Exception as error:
            cursor.execute("ROLLBACK")
            conn.commit()
            return f'ERROR: {error}'

        return dbc.Table.from_dataframe(
                            df,
                            id = 'data_SQL_table',
                            striped=True,
                            bordered=True,
                            hover=True)

# @app.callback([
#     Output('data_SQL_download_button','children'),
#     Output('data_SQL_table_div','children')],[
#     Input('data_SQL_download_button','n_clicks'),
#     State('SQL_input','value')
#     ])
# def data_SQL_download_function(n_clicks, query_string):

#     # print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
#     if n_clicks:
#         try:
#             data_SQL_download(cursor, query_string)
#         except Exception as error:
#             cursor.execute("ROLLBACK")
#             conn.commit()
#             return 'Descargar', f'ERROR: {error}'

#         return 'Descargar', 'Archivo descargado'


@app.callback(
    Output('data_prices_nodes_dopdown','options'),
    Input('data_prices_zona_de_carga_dopdown','value')
    )
def get_nodes_from_zones(zones):

    zones = ("','").join(zones)
    cursor.execute("""SELECT clave_nodo FROM nodes_info WHERE zona_de_carga in ('{}');""".format(zones))
    nodos = [nodo[0] for nodo in cursor.fetchall()]
    print(len(nodos))

    options = [{'label': nodo, 'value': nodo} for nodo in nodos]

    return options

@app.callback(
    Output('data_prices_nodes_dopdown','disabled'),
    Input('data_prices_zone_or_node_dopdown','value')
    )
def disable_data_nodes_dropdown(zonas_nodos):

    if zonas_nodos == 'zones':
        return True
    else:
        return False





if __name__ == '__main__':
    app.run_server()
    # pass