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



db_name = 'cenace'


conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
cursor = conn.cursor()

cursor.execute("""SELECT DISTINCT(zona_de_carga) FROM consumption_real;""")
zonas_de_carga = [zona[0] for zona in cursor.fetchall()]
zonas_de_carga.append('MEXICO (PAIS)')

zones_list = {'sin':get_zones_list(cursor, system='sin', market='mda'),
            'bca':get_zones_list(cursor, system='bca', market='mda'),
            'bcs':get_zones_list(cursor, system='bcs', market='mda')}


app = dash.Dash()


app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Generation & Consumption', children=[
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
            html.Div(
                dcc.RadioItems(
                    id = 'graph_type',
                    options=[
                        {'label': 'Normal Graph', 'value': False},
                        {'label': 'Hourly Average Per Month', 'value': True}
                        ],
                    value='False'
                    )),
            html.Div(
                dcc.Dropdown(
                    id = 'zona_de_carga_dopdown',
                    options = [{'label': zona, 'value': zona} for zona in zonas_de_carga],
                    multi = True,
                    placeholder = "Select a Node",
                    value = ['OAXACA','CAMPECHE','ACAPULCO','PUEBLA'])
                ),
            html.Div(
                dcc.Graph(
                    id = 'daily_consumption_graph',
                    figure = consumption_daily(cursor)
                    ),
                )
            ]),
        dcc.Tab(label='Zone Marginal Prices', children=[
            html.Div(
                dcc.Dropdown(
                    id = 'system_dropdown',
                    options = [
                        {'label': 'SIN', 'value': 'sin'},
                        {'label': 'BCA', 'value': 'bca'},
                        {'label': 'BCS', 'value': 'bcs'}],
                    placeholder = "Select a system",
                    value = 'sin'),
                style = {'width': '10%', 'display': 'inline-block'}
                ),
            html.Div(
                dcc.Dropdown(
                    id = 'market_dropdown',
                    options = [
                        {'label': 'MDA', 'value': 'mda'},
                        {'label': 'MTR', 'value': 'mtr'}],
                    placeholder = "Select a market",
                    value = 'mda'),
                style = {'width': '10%', 'display': 'inline-block'}
                ),
            html.Div(
                dcc.Dropdown(
                    id = 'zona_de_carga_prices_dopdown',
                    options = [{'label': zona, 'value': zona} for zona in zones_list['sin']],
                    placeholder = "Select a Node",
                    value = 'OAXACA'),
                style = {'width': '80%', 'display': 'inline-block'}
                ),
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
            html.Div(
                dcc.RadioItems(
                    id = 'graph_type2',
                    options=[
                        {'label': 'Normal Graph', 'value': False},
                        {'label': 'Hourly Average Per Month', 'value': True}
                        ],
                    value='False'
                    )),
            html.Div(
                dcc.Dropdown(
                    id = 'zona_de_carga_dopdown2',
                    options = [{'label': zona, 'value': zona} for zona in zonas_de_carga],
                    multi = True,
                    placeholder = "Selecciona una zona de carga",
                    value = ['OAXACA','CAMPECHE','ACAPULCO','PUEBLA'])
                ),
            html.Div(
                dcc.Graph(
                    id = 'daily_consumption_graph2',
                    figure = consumption_daily(cursor)
                    ),
                )
            ])
        ])
    ])

@app.callback(
    Output('daily_consumption_graph', 'figure'),
    Input('zona_de_carga_dopdown','value'))
def daily_consumption_graph_function(value):
    fig = consumption_daily(cursor,value)
    return fig

@app.callback(
    Output('daily_generation_graph', 'figure'),
    Input('graph_type','value'))
def daily_generation_graph_function(value):
    if value:
        fig = generation_month_hourly_average(cursor)
    else:
        fig = generation_daily(cursor)
    return fig

@app.callback(
    Output('hourly_generation_graph', 'figure'),
    Input('daily_generation_graph', 'clickData'))
def hourly_generation_graph_function(clickData):
    print(clickData)
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
    Input('market_dropdown','value')])
def zone_options_pnd(system, market):

    zone_list = zones_list[system]
    return [{'label': zone, 'value': zone} for zone in zone_list]


@app.callback(
    Output('zone_daily_price_graph', 'figure'),
    [Input("system_dropdown", "value"),
    Input('market_dropdown','value'),
    Input('zona_de_carga_prices_dopdown','value')])
def daily_zone_prices_graph_function(system, market, zone):
    print('\n\n\n')
    print(system, market, zone)
    if not zone:
        return 0
    fig = zone_daily_prices(cursor,system, market, zone)

    return fig

@app.callback(
    Output('zone_hourly_price_graph', 'figure'),[
    Input('zone_daily_price_graph', 'clickData'),
    Input("system_dropdown", "value"),
    Input('market_dropdown','value'),
    Input('zona_de_carga_prices_dopdown','value')])
def hourly_zone_prices_graph_function(clickData, system, market, zone):
    print(clickData, '\n\n\n\n\n\n\n\n\n\n')
    days, date = 10 , []
    if clickData:
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') - datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') + datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        fig = zone_hourly_prices(cursor,system, market, zone, date)
    else:
        fig = zone_hourly_prices(cursor)

    return fig




if __name__ == '__main__':
    app.run_server()
    # pass