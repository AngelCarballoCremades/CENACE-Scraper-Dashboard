import plotly.express as px
import pandas as pd
import numpy as np
import psycopg2 as pg2
import os
import sys
from functions import *
import datetime
from shapely.geometry import Point


def generation_daily(cursor):

    print('requesting daily generation...')

    try:
        cursor.execute("""
            SELECT * FROM generation_real
            ORDER BY
                fecha ASC,
                hora ASC
            ;""")
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['fecha'] = pd.to_datetime(df['fecha'])

    for col in df.columns:
        if col not in ['sistema','fecha','hora']:
            df[col] = df[col].astype('float')

    df_filtered = df.groupby(['fecha']).sum()
    df_filtered.drop(columns=['hora'], inplace=True)
    df_filtered = df_filtered.stack().to_frame()
    df_filtered.reset_index(inplace=True)
    df_filtered.columns = ['fecha','gen_type','generation_mwh']

    fig = px.area(
        data_frame=df_filtered,
        x="fecha",
        y="generation_mwh",
        color="gen_type",
        hover_data=['gen_type','generation_mwh'],
        category_orders=dict(
            gen_type = [
                'nucleoelectrica',
                'carboelectrica',
                'combustion_interna',
                'ciclo_combinado',
                'geotermoelectrica',
                'termica_convencional',
                'turbo_gas',
                'hidroelectrica',
                'biomasa',
                'eolica',
                'fotovoltaica'
                ]))
    fig.update_layout(clickmode='event+select')
    fig.update_layout(
        title= dict(
            text = "Generación Real Por Día",
            x = 0.5),
        xaxis_title=None,
        yaxis_title="Generación [MWh]",
        xaxis_ticks = 'outside',
        yaxis_ticks = 'outside',
        legend_title=None,
        font=dict(
            family="Arial",
            size=12.5))
    return fig



def generation_month_hourly_average(cursor):

    print('requesting hourly generation...')

    try:
        cursor.execute("""
            SELECT * FROM generation_real
            ORDER BY
                fecha ASC,
                hora ASC
            ;""")
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df = df[df.hora != 25]
    df['fecha'] = pd.to_datetime(df['fecha'])

    for col in df.columns:
        if col not in ['sistema','fecha','hora']:
            df[col] = df[col].astype('float')

    df['total_gen'] = sum([df[col] for col in df.columns if col not in ['sistema','fecha','hora']])
    df['year'] = df.fecha.apply(lambda x: x.year)
    df['month'] = df.fecha.apply(lambda x: x.month)

    df_filtered = df.groupby(['year','month','hora']).mean()
    df_filtered.reset_index(inplace=True)
    df_filtered = df_filtered[['year','month','hora','total_gen']]
    df_filtered['month_hour'] =  df_filtered['month'].astype('str')+' '+df_filtered['hora'].astype('str')
    df_filtered['month_hour'] = df_filtered['month_hour'].apply(lambda x: datetime.datetime.strptime(x, '%m %d'))

    fig = px.line(
        data_frame=df_filtered,
        x="month_hour",
        y="total_gen",
        color="year",
        hover_data=['total_gen','month','hora'],
        )
    fig.update_layout(clickmode='event+select')
    fig.update_layout(template="plotly_white")
    fig.update_xaxes(tickformat="%b")# %b\n%Y
    return fig


def generation_hourly(cursor, dates = 0):

    print('requesting hourly generation...')

    if not dates:
        try:
            cursor.execute("""
                SELECT * FROM generation_real
                WHERE
                    fecha = (SELECT MAX(fecha) FROM generation_real)
                ORDER BY
                    fecha ASC,
                    hora ASC
                ;""")
        except:
            cursor.execute("ROLLBACK")
            pass

    elif type(dates) == type([]):
        try:
            cursor.execute("""
                SELECT * FROM generation_real
                WHERE
                    fecha BETWEEN '{}' AND '{}'
                ORDER BY
                    fecha ASC,
                    hora ASC
                ;""".format(dates[0],dates[1]))
        except:
            cursor.execute("ROLLBACK")
            pass

    colnames = [desc[0] for desc in cursor.description]
    df_hourly = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df_hourly['fecha'] = pd.to_datetime(df_hourly['fecha'])
    df_hourly['fecha'] +=  pd.to_timedelta(df_hourly.hora, unit='h')
    df_hourly.drop(columns=['hora'], inplace=True)

    for col in df_hourly.columns:
        if col not in ['sistema','fecha','hora']:
            df_hourly[col] = df_hourly[col].astype('float')

    df_hourly = df_hourly.groupby(['fecha']).sum()
    df_hourly = df_hourly.stack().to_frame()
    df_hourly.reset_index(inplace=True)
    df_hourly.columns = ['fecha','gen_type','generation_mwh']

    fig = px.area(
        data_frame=df_hourly,
        x='fecha',
        y="generation_mwh",
        color="gen_type",
        hover_data=['gen_type','generation_mwh'],
        category_orders=dict(
            gen_type = [
                'nucleoelectrica',
                'carboelectrica',
                'combustion_interna',
                'ciclo_combinado',
                'geotermoelectrica',
                'termica_convencional',
                'turbo_gas',
                'hidroelectrica',
                'biomasa',
                'eolica',
                'fotovoltaica'
                ]),
        )
    fig.update_layout(
        title= dict(
            text = "Generación Real Por Hora",
            x = 0.5),
        xaxis_title=None,
        yaxis_title="Generación [MWh]",
        xaxis_ticks = 'outside',
        yaxis_ticks = 'outside',
        legend_title=None,
        font=dict(
            family="Arial",
            size=12.5))

    return fig


def consumption_daily(cursor, zonas_de_carga = ['OAXACA']):

    print('requesting zonas...')
    total = False
    if zonas_de_carga == ['MEXICO (PAIS)']:
        total = True

    if total:
        try:
            cursor.execute("""
                SELECT fecha, SUM(energia) AS energia FROM consumption_real
                GROUP BY fecha
                ORDER BY
                    fecha ASC
                ;""")
        except:
            cursor.execute("ROLLBACK")
            pass

    else:
        zonas_string = "','".join([zona for zona in zonas_de_carga])

        try:
            cursor.execute("""
                SELECT * FROM consumption_real
                WHERE zona_de_carga in ('{}')
                ORDER BY
                    fecha ASC,
                    hora ASC
                ;""".format(zonas_string))
        except:
            cursor.execute("ROLLBACK")
            pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['energia'] = df['energia'].astype('float')

    if total:
        fig = px.line(
            data_frame=df,
            x="fecha",
            y="energia",
            )

        fig.update_layout(clickmode='event+select')
        fig.update_layout(template="plotly_white")
        return fig

    if not total:
        df_filtered = df.groupby(['fecha','zona_de_carga']).sum()
        df_filtered.drop(columns=['hora'], inplace=True)
        df_filtered.reset_index(inplace=True)
        df_filtered.columns = ['fecha','zona_de_carga','energia']

        fig = px.line(
            data_frame=df_filtered,
            x="fecha",
            y="energia",
            color="zona_de_carga",
            hover_data=['zona_de_carga','energia']
            )

        fig.update_layout(clickmode='event+select')
        fig.update_layout(
            title= dict(
                text = "Consumo Real En Zonas De Carga Por Día",
                x = 0.5),
            xaxis_title=None,
            yaxis_title="Consumo [MWh]",
            xaxis_ticks = 'outside',
            yaxis_ticks = 'outside',
            legend_title=None,
            font=dict(
                family="Arial",
                size=12.5))
        return fig


def zone_daily_prices(cursor, market='mda', zone='OAXACA'):

    print('requesting prices...', zone)
    try:
        cursor.execute("""
            SELECT sistema FROM nodes_info
            WHERE zona_de_carga = '{}'
            LIMIT 1
            ;""".format(zone))
    except:
        cursor.execute("ROLLBACK")
        pass

    system = cursor.fetchall()[0][0]

    try:
        cursor.execute("""
            SELECT * FROM {}_pnd_{}
            WHERE zona_de_carga = '{}'
            ORDER BY
                fecha ASC,
                hora ASC
            ;""".format(system,market, zone))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.drop(columns=['hora','sistema','mercado','zona_de_carga'], inplace=True)

    for col in ['c_energia','c_perdidas','c_congestion','precio_e']:
        df[col] = df[col].astype('float')

    df = df.groupby(['fecha', 'precio_e']).mean()
    df = df.stack().to_frame()
    df.reset_index(inplace=True)
    df.columns = ['fecha','precio_e','price_component','$/MWh']
    df = df.groupby(['fecha','price_component']).mean()
    df.reset_index(inplace=True)

    fig = px.area(
        data_frame=df,
        x='fecha',
        y="$/MWh",
        color="price_component",
        hover_data=['price_component','$/MWh','precio_e'],
        category_orders=dict(
            price_component = [
                'c_energia',
                'c_perdidas',
                'c_congestion'
                ])
        )
    fig.update_layout(template="plotly_white")
    fig.update_layout(
        title= dict(
            text = f'Precio (PND) Promedio Por Día - {zone} - {market.upper()}',
            x = 0.5),
        xaxis_title=None,
        yaxis_title="Precio [$/MWh]",
        xaxis_ticks = 'outside',
        yaxis_ticks = 'outside',
        legend_title=None,
        font=dict(
            family="Arial",
            size=12.5))
    return fig


def zone_hourly_prices(cursor, market='mda', zone='OAXACA', dates = 0):

    print('requesting zone hourly prices...')

    try:
        cursor.execute("""
            SELECT sistema FROM nodes_info
            WHERE zona_de_carga = '{}'
            LIMIT 1
            ;""".format(zone))
    except:
        cursor.execute("ROLLBACK")
        pass

    system = cursor.fetchall()[0][0].lower()
    print('system {}'.format(system))

    if not dates:
        try:
            cursor.execute("""
                SELECT * FROM {}_pnd_{}
                WHERE
                    zona_de_carga = '{}' AND
                    fecha = (SELECT MAX(fecha) from {}_pnd_{})
                ORDER BY
                    fecha ASC,
                    hora ASC
                ;""".format(system,market, zone, system, market))
        except:
            cursor.execute("ROLLBACK")
            pass

    elif type(dates) == type([]):
        try:
            cursor.execute("""
                SELECT * FROM {}_pnd_{}
                WHERE
                    zona_de_carga = '{}' AND
                    fecha BETWEEN '{}' AND '{}'
                ORDER BY
                    fecha ASC,
                    hora ASC
                ;""".format(system,market, zone, dates[0], dates[1]))
        except:
            cursor.execute("ROLLBACK")
            pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['fecha'] +=  pd.to_timedelta(df.hora, unit='h')
    df.drop(columns=['hora'], inplace=True)

    for col in ['c_energia','c_perdidas','c_congestion','precio_e']:
        df[col] = df[col].astype('float')

    df = df.groupby(['fecha', 'precio_e']).mean()
    df = df.stack().to_frame()
    df.reset_index(inplace=True)

    df.columns = ['fecha','precio_e','price_component','$/MWh']

    fig = px.area(
        data_frame=df,
        x='fecha',
        y="$/MWh",
        color="price_component",
        hover_data=['price_component','$/MWh','precio_e'],
        category_orders=dict(
            price_component = [
                'c_energia',
                'c_perdidas',
                'c_congestion'
                ])
        )
    fig.update_layout(
        title= dict(
            text = f'Precio (PND) Promedio Por Hora - {zone} - {market.upper()}',
            x = 0.5),
        xaxis_title=None,
        yaxis_title="Precio [$/MWh]",
        xaxis_ticks = 'outside',
        yaxis_ticks = 'outside',
        legend_title=None,
        font=dict(
            family="Arial",
            size=12.5))
    return fig


def marginal_prices(cursor, zona_de_carga = 'OAXACA', market = 'mda', data = 'precio_e', graph_type = 'real'):

    print('requesting marginal prices...')

    try:
        cursor.execute("""
            SELECT sistema FROM nodes_info
            WHERE zona_de_carga = '{}'
            LIMIT 1
            ;""".format(zona_de_carga))
    except:
        cursor.execute("ROLLBACK")
        pass

    system = cursor.fetchall()[0][0]

    print('...requesting nodes data...')
    try:
        cursor.execute("""
            SELECT
                fecha,
                main.clave_nodo AS clave_nodo,
                AVG({}) AS {}
            FROM {}_pml_{} AS main
            INNER JOIN nodes_info AS inf
                ON main.clave_nodo = inf.clave_nodo
            WHERE zona_de_carga = '{}'
            GROUP BY
                fecha,
                main.clave_nodo
            ORDER BY
                fecha ASC,
                clave_nodo ASC
            ;""".format(data, data, system, market, zona_de_carga))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df[data] = df[data].astype('float')

    print('...requesting zone data...')
    try:
        cursor.execute("""
            SELECT
                fecha,
                zona_de_carga AS clave_nodo,
                AVG({}) AS {}
            FROM {}_pnd_{}
            WHERE zona_de_carga = '{}'
            GROUP BY
                fecha,
                zona_de_carga
            ORDER BY
                fecha ASC
            ;""".format(data, data, system,market, zona_de_carga))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df2 = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df2['fecha'] = pd.to_datetime(df2['fecha'])

    if graph_type == 'percent':
        df2[data] = df2[data].astype('float')
        df = pd.merge(left=df, right=df2, on='fecha', how='left')
        df['Difference (%)'] = ((df[f'{data}_x'] - df[f'{data}_y'])/df[f'{data}_y'])*100
        df.columns = ['fecha','clave_nodo',f'{data}_node','zona_de_carga',f'{data}_zona_de_carga','Difference %']
        df.drop(columns = 'zona_de_carga', inplace=True)

    elif graph_type == 'real':
        df = pd.concat([df2, df])

    print('Requesting info...')
    try:
        cursor.execute("""
            SELECT
                clave_nodo,
                nombre_nodo,
                zona_de_carga,
                nodop_nivel_de_tensión_kv AS tension_kv,
                ubicación_entidad_federativa AS entidad_federativa,
                ubicación_municipio AS municipio
            FROM nodes_info
            WHERE zona_de_carga = '{}'
            ;""".format(zona_de_carga))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df_info = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df = pd.merge(left=df, right=df_info, on='clave_nodo', how='left')
    df.fillna('---')

    titulos = {
        'precio_e':'Precio Total  De Energía',
        'c_energia':'Componente de Energía',
        'c_perdidas':'Componente de Pérdidas',
        'c_congestion':'Componente de Congestión',}

    if graph_type == 'percent':
        fig = px.line(
            data_frame=df,
            x="fecha",
            y="Difference %",
            color="clave_nodo",
            hover_data=colnames
            )
        fig.update_layout(
            title_text = f'Diferencia De Precio de Nodo Distribuido ({zona_de_carga}) y Precios Marginales Locales - {titulos[data]} - {market.upper()}',
            yaxis_title="Diferencia [%]")


    elif graph_type == 'real':
        fig = px.line(
            data_frame=df,
            x="fecha",
            y=f"{data}",
            color="clave_nodo",
            hover_data=colnames
            )
        fig.update_layout(
            title_text = f'Histórico De Precio de Nodo Distribuido ({zona_de_carga}) y Precios Marginales Locales - {titulos[data]} - {market.upper()}',
            yaxis_title="Precio [$/MWh]")

    fig.update_layout(clickmode='event+select')
    fig.update_layout(
        title_x = 0.5,
        xaxis_title=None,
        xaxis_ticks = 'outside',
        yaxis_ticks = 'outside',
        legend_title=None,
        font=dict(
            family="Arial",
            size=12.5))

    return fig


def zones_prices(cursor, zones = [], zone = 'OAXACA', market='mda', data = 'precio_e'):

    if not zones:
        zones = [zone]

    if zone in zones:
        pass
    else:
        zones.append(zone)

    zones = "','".join(zones)

    print('requesting prices...', zones)

    dfs = []
    for system in ['sin','bca','bcs']:

        try:
            cursor.execute("""
                SELECT
                    fecha,
                    zona_de_carga,
                    AVG({}) AS {}
                FROM {}_pnd_{}
                WHERE zona_de_carga in ('{}')
                GROUP BY
                    fecha,
                    zona_de_carga
                ORDER BY
                    fecha ASC
                ;""".format(data, data, system, market, zones))
        except:
            cursor.execute("ROLLBACK")
            pass

        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
        dfs.append(df)

    df = pd.concat(dfs)

    df['fecha'] = pd.to_datetime(df['fecha'])
    df[data] = df[data].astype('float')

    titulos = {
        'precio_e':'Precio Total  De Energía',
        'c_energia':'Componente de Energía',
        'c_perdidas':'Componente de Pérdidas',
        'c_congestion':'Componente de Congestión',}


    fig = px.line(
        data_frame=df,
        x='fecha',
        y=f"{data}",
        color="zona_de_carga",
        hover_data=['fecha','zona_de_carga',f'{data}']
        )
    fig.update_layout(template="plotly_white")
    fig.update_layout(
        title= dict(
            text = f'Comparación de Precio {titulos[data]} Promedio Por Día - {market.upper()}',
            x = 0.5),
        xaxis_title=None,
        yaxis_title="Precio [$/MWh]",
        xaxis_ticks = 'outside',
        yaxis_ticks = 'outside',
        legend_title=None,
        font=dict(
            family="Arial",
            size=12.5))
    return fig


def locate_close_nodes(cursor, latitud = None, longitud = None, number_of_nodes=5, mapbox_style="open-street-map", zoom = 7):


    if not (latitud and longitud):

        latitud = '23.769457'
        longitud = '-102.507216'
        zoom = 4

        fig = px.scatter_mapbox(
            lat=[0],
            lon=[0],
            zoom=zoom,
            height=500,
            center = dict(
                lat = float(latitud),
                lon = float(longitud))
            )

        fig.update_layout(mapbox_style=mapbox_style)
        fig.update_layout(coloraxis_showscale=False)
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig


    cursor.execute("""SELECT * FROM nodes_info""")

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    lats = [float(row[-2]) if row[-2] != '' else 0 for row in df.values]
    lons = [float(row[-1]) if row[-1] != '' else 0 for row in df.values]

    df['Points'] = [Point(lat,lon) for lat, lon in zip(lats,lons)]

    selected_point = Point(float(latitud), float(longitud))

    distances = [p.distance(selected_point) for p in df.Points.values]

    df['distance'] = distances

    df.sort_values(by='distance', axis = 0, ascending=True, inplace=True)

    distances_ordered = sorted(list(set(distances)))

    df_final = pd.DataFrame(columns = df.columns)

    largo = df_final.copy()
    while largo.shape[0] < number_of_nodes and largo.shape[0] < df.shape[0]:
        largo = pd.concat([largo,df[df.distance == distances_ordered[0]]])
        df_final = df_final.append(df[df.distance == distances_ordered.pop(0)].iloc[0])

    edo_mun = df_final['ubicación_entidad_federativa'] + '___' + df_final['ubicación_municipio']

    lista_nodos = []
    estados = []
    municipios = []

    for e_m in edo_mun.unique():
        estado = e_m.split('___')[0]
        municipio = e_m.split('___')[1]
        estados.append(estado)
        municipios.append(municipio)

        try:
            cursor.execute("""
                SELECT
                    clave_nodo,
                    nombre_nodo
                FROM nodes_info
                WHERE
                    ubicación_entidad_federativa = '{}' AND
                    ubicación_municipio = '{}'
                ;""".format(estado, municipio))
        except:
            cursor.execute("ROLLBACK")
            pass

        lista_nodos.append([f'<br>{node[0]}/{node[1]}' for node in cursor.fetchall()])

    edos_muns = '-<span style="display: none">'+('___').join([ ('_').join(couple) for couple in list(zip(estados, municipios)) ])+'</span>'

    df_final['nodos'] = lista_nodos
    df_final['color'] = 1
    selected_point_df = pd.DataFrame.from_dict(data = {
                                                    'lat':[latitud],
                                                    'lon':[longitud],
                                                    'color': [500],
                                                    'nodos':[edos_muns],
                                                    'ubicación_entidad_federativa':'-',
                                                    'ubicación_municipio':'-'}, orient = 'columns')
    df_final = df_final.append(selected_point_df)
    df_final['marker_size'] = 12

    fig = px.scatter_mapbox(df_final,
        lat=df_final['lat'].astype('float'),
        lon=df_final['lon'].astype('float'),
        size = 'marker_size',
        color = 'color',
        color_discrete_sequence=["identity"],
        zoom=zoom,
        height=500,
        center = dict(
            lat = float(latitud),
            lon = float(longitud)),
        hover_data = {
            'ubicación_entidad_federativa':True,
            'ubicación_municipio':True,
            'color':False,
            'marker_size':False,
            'nodos':True
            }
        )

    fig.update_layout(mapbox_style=mapbox_style)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

if __name__ == '__main__':
    pass