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



app = dash.Dash()


app.layout = html.Div([
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
            # labelStyle={'display': 'inline-block'}
            )),
    html.Div(
        dcc.Dropdown(
            id = 'zona_de_carga_dopdown',
            options = [{'label': zona, 'value': zona} for zona in zonas_de_carga],
            multi = True,
            placeholder = "Selecciona una zona de carga",
            value = ['OAXACA','CAMPECHE','ACAPULCO','PUEBLA'])
        ),
    html.Div(
        dcc.Graph(
            id = 'daily_consumption_graph',
            figure = consumption_daily(cursor)
            ),
        ),
    ])


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])

@app.callback(
    Output('daily_consumption_graph', 'figure'),
    Input('zona_de_carga_dopdown','value'))
def zona_de_carga_function(value):
    fig = consumption_daily(cursor,value)
    return fig

@app.callback(
    Output('daily_generation_graph', 'figure'),
    Input('graph_type','value'))
def zona_de_carga_function(value):
    if value:
        fig = generation_month_hourly_average(cursor)
    else:
        fig = generation_daily(cursor)
    return fig

@app.callback(
    Output('hourly_generation_graph', 'figure'),
    Input('daily_generation_graph', 'clickData'))
def update_hourly_gen_graph(clickData):
    print(clickData)
    days, date = 10 , []
    if clickData:
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') - datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        date.append((datetime.datetime.strptime(clickData['points'][0]['x'], '%Y-%m-%d') + datetime.timedelta(days=days)).strftime('%Y-%m-%d'))
        fig = generation_hourly(cursor,date)
    else:
        fig = generation_hourly(cursor)

    return fig




if __name__ == '__main__':
    app.run_server()
    # pass