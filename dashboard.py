import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import psycopg2 as pg2
from functions import *
import datetime
from dashboard_graphs import *
import plotly.io as pio
import dash_bootstrap_components as dbc


pio.templates.default = "plotly_white"
db_name = 'cenace'


conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
cursor = conn.cursor()

cursor.execute("""SELECT DISTINCT(zona_de_carga) FROM consumption_real;""")
zonas_de_carga = [zona[0] for zona in cursor.fetchall()]
zonas_de_carga.append('MEXICO (PAIS)')

zones_list = {'sin':get_zones_list(cursor, system='sin', market='mda'),
            'bca':get_zones_list(cursor, system='bca', market='mda'),
            'bcs':get_zones_list(cursor, system='bcs', market='mda')}


style1 = {'font-family': 'Arial', 'font-size': '150%'}
style0 = {'text-align':'center','font-family': 'Arial', 'font-size': '100%'}
dropdown_style = {'width': '28%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}
dropdown_style_2 = {'width': '28%', 'display': 'inline-block', 'font-family': 'Arial', 'vertical-align': 'middle'}

app = dash.Dash(__name__, title='Energía de México', update_title='Cargando...', external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div(html.Center(html.Div([
    html.Div(dcc.Markdown('# **Dashboard de Energía en México**'),
        style = style0
        ),
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
                            value = ['OAXACA','CAMPECHE','ACAPULCO','PUEBLA'],
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
                    ])
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
                # html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                # html.Div(
                #     dcc.Dropdown(
                #         id = 'price_graph_comparisson_dropdown',
                #         options = [
                #             {'label': 'Precio Total de Energía', 'value': 'precio_e'},
                #             {'label': 'Componente de Energía', 'value': 'c_energia'},
                #             {'label': 'Componente de Pérdidas', 'value': 'c_perdidas'},
                #             {'label': 'Componente de Congestión', 'value': 'c_congestion'}],
                #         multi = False,
                #         value = 'precio_e',
                #         clearable=False,
                #         style = {'text-align':'center'}),
                #     style = dropdown_style
                #     ),
                html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
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
                    style = dropdown_style
                    ),
                html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
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
                    style = dropdown_style
                    ),
                html.Div([], style = {'width': '4%', 'display': 'inline-block'}),
                html.Div(html.P()),
                dcc.Loading(
                        id="loading_element_prices",
                        type="circle",
                        children=[html.Div(
                            dcc.Graph(
                                id = 'marginal_prices_graph',
                                figure = marginal_prices(cursor)
                                ),
                        )]
                    )
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
                    )
                ]
            )
        ]
        )
    ],
    style = {'width': '95%'}
    )))

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
    Output('marginal_prices_graph', 'figure'),[
    Input('price_component_graph_type_dropdown','value'),
    Input('price_component_dropdown', 'value'),
    State('zona_de_carga_prices_dopdown', 'value'),
    State("system_dropdown", "value"),
    State('market_dropdown','value')])
def marginal_prices_graph_function(graph_type, data, zona_de_carga, system, market):

    fig = marginal_prices(cursor, zona_de_carga, system, market, data, graph_type)
    return fig

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




if __name__ == '__main__':
    app.run_server()
    # pass