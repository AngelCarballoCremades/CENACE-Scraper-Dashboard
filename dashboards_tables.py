import pandas as pd
import numpy as np
import psycopg2 as pg2
import os
import sys
from functions import *
import datetime



def map_click_table(cursor, estado, municipio = None, node_info = False):

    if not municipio:
        estados = estado.replace('-<span style="display: none">','').replace('</span>','').split('___')
        edos_muns = [p.split('_') for p in estados]

    else:
        edos_muns = [[estado, municipio]]

    dfs = []

    for estado, municipio in edos_muns:
        cursor.execute("""
            SELECT
                ubicación_entidad_federativa,
                ubicación_municipio,
                clave_nodo,
                nombre_nodo
            FROM nodes_info
            WHERE
                ubicación_entidad_federativa = '{}' AND
                ubicación_municipio = '{}'
                ;""".format(estado, municipio))

        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
        dfs.append(df)

    df_nodos = pd.concat(dfs)

    nodos = df_nodos.clave_nodo.unique()
    nodos = ("','").join(nodos)
    year = datetime.datetime.now().year
    dfs = []

    for system in ['sin','bca','bcs']:
        print(f'requesting {system}...')
        cursor.execute("""
                SELECT
                    clave_nodo,
                    MAX(precio_e) AS precio_maximo,
                    MIN(precio_e) AS precio_minimo,
                    AVG(precio_e) AS precio_promedio,
                    STDDEV_POP(precio_e) AS desviacion_estandar
                FROM {}_pml_mtr
                WHERE
                    clave_nodo in ('{}') AND
                    EXTRACT(YEAR FROM fecha) = {}
                GROUP BY clave_nodo
                ;""".format(system, nodos, year))

        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
        dfs.append(df)

    df_data = pd.concat(dfs)
    df_data[['precio_maximo', 'precio_minimo', 'precio_promedio', 'desviacion_estandar']] = df_data[['precio_maximo', 'precio_minimo', 'precio_promedio', 'desviacion_estandar']].astype('float').round(2)

    df = pd.merge(left = df_nodos, right = df_data, on='clave_nodo')

    return df


def prices_zones_table(cursor, system, market, zone, zones, price_component):

    if not zones:
        zones = [zone]

    if zone in zones:
        pass
    else:
        zones.append(zone)

    zones = "','".join(zones)
    year = datetime.datetime.now().year

    print(f'requesting zones table...')
    cursor.execute("""
            SELECT
                zona_de_carga,
                MAX({}) AS precio_maximo,
                MIN({}) AS precio_minimo,
                AVG({}) AS precio_promedio,
                STDDEV_POP({}) AS desviacion_estandar
            FROM {}_pnd_{}
            WHERE
                zona_de_carga in ('{}') AND
                EXTRACT(YEAR FROM fecha) = {}
            GROUP BY zona_de_carga
            ;""".format(price_component, price_component, price_component, price_component, system, market, zones, year))

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    for col in df.columns:
        if col != 'zona_de_carga':
            df[col] = df[col].astype('float').round(2)

    return df


def prices_nodes_table(cursor, system, market, zona_de_carga, price_component):

    year = datetime.datetime.now().year

    print('requesting nodes prices...')
    cursor.execute("""
        SELECT
            main.clave_nodo AS clave_nodo,
            MAX({}) AS precio_maximo,
            MIN({}) AS precio_minimo,
            AVG({}) AS precio_promedio,
            STDDEV_POP({}) AS desviacion_estandar
        FROM {}_pml_{} AS main
        INNER JOIN nodes_info AS inf
            ON main.clave_nodo = inf.clave_nodo
        WHERE
            zona_de_carga = '{}' AND
            EXTRACT(YEAR FROM fecha) = {}
        GROUP BY
            main.clave_nodo
        ;""".format(price_component, price_component, price_component, price_component, system, market, zona_de_carga, year))

    colnames = [desc[0] for desc in cursor.description]
    df_nodes = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    print('...')
    cursor.execute("""
        SELECT
            zona_de_carga AS clave_nodo,
            MAX({}) AS precio_maximo,
            MIN({}) AS precio_minimo,
            AVG({}) AS precio_promedio,
            STDDEV_POP({}) AS desviacion_estandar
        FROM {}_pnd_{}
        WHERE
            zona_de_carga = '{}' AND
            EXTRACT(YEAR FROM fecha) = {}
        GROUP BY zona_de_carga
        ;""".format(price_component, price_component, price_component, price_component, system, market, zona_de_carga, year))

    colnames = [desc[0] for desc in cursor.description]
    df_zone = pd.DataFrame(data=cursor.fetchall(), columns=colnames)


    df = pd.concat([df_zone, df_nodes])


    for col in df.columns:
        if col != 'clave_nodo':
            df[col] = df[col].astype('float').round(2)

    # print(df_nodes.T)
    # print(df_zone.T)
    # print(df.T)


    return df


def data_generation_preview(cursor,start_date, end_date, data):

    print('requesting generation data...')

    cursor.execute("""
        SELECT * FROM generation_{}
        WHERE
            fecha >= '{}' AND
            fecha <= '{}'
        LIMIT 50;""".format(data, start_date, end_date))

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    for col in df.columns:
        if col not in ['sistema','fecha','hora']:
            df[col] = df[col].astype('float').round(2)

    return df


def data_consumption_preview(cursor,start_date, end_date, data, zones):

    print('requesting consumption data...')

    if zones == ['MEXICO (PAIS)']:
        cursor.execute("""
            SELECT * FROM consumption_{}
            WHERE
                fecha >= '{}' AND
                fecha <= '{}'
            LIMIT 50;""".format(data, start_date, end_date))

    else:
        zones = ("','").join(zones)

        cursor.execute("""
            SELECT * FROM consumption_{}
            WHERE
                fecha >= '{}' AND
                fecha <= '{}' AND
                zona_de_carga in ('{}')
            LIMIT 50;""".format(data, start_date, end_date, zones))


    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    # print(df)

    df['energia'] = df['energia'].astype('float')

    return df



def data_prices_preview(cursor,start_date, end_date, market, zonas_nodos, zones, nodes):

    print('requesting prices data...')
    if not zones:
        return pd.DataFrame()

    dfs = []

    if zonas_nodos == 'zones':

        zones = ("','").join(zones)

        for system in ['sin','bca','bcs']:

            cursor.execute("""
                SELECT * FROM {}_pnd_{}
                WHERE
                    fecha >= '{}' AND
                    fecha <= '{}' AND
                    zona_de_carga in ('{}')
                LIMIT 30;""".format(system, market, start_date, end_date, zones))

            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
            dfs.append(df)

        df = pd.concat(dfs)
        # print(df)
        return df

    else:
        nodes = ("','").join(nodes)

        for system in ['sin','bca','bcs']:
            cursor.execute("""
                SELECT * FROM {}_pml_{}
                WHERE
                    fecha >= '{}' AND
                    fecha <= '{}' AND
                    clave_nodo in ('{}')
                LIMIT 30;""".format(system, market, start_date, end_date, nodes))


            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
            dfs.append(df)

        df = pd.concat(dfs)
        # print(df)
        return df


def data_SQL_preview(cursor,query_string):

    print('requesting SQL data...')

    cursor.execute(query_string)

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    return df


def data_generation_download(cursor,start_date, end_date, data):

    print('downloading generation data...')

    query_string = """SELECT * FROM generation_{} WHERE fecha >= '{}' AND fecha <= '{}'""".format(data, start_date, end_date)

    SQL_for_file_output = "COPY ({}) TO STDOUT WITH CSV HEADER".format(query_string)

    file_name = get_download_file_name(f'generacion_{data}_{start_date[:10]}_{end_date[:10]}')

    file_path = f"..\\files\\descargas\\{file_name}"

    with open(file_path, 'w') as f:
        cursor.copy_expert(SQL_for_file_output, f)


def data_consumption_download(cursor,start_date, end_date, data, zones):

    print('downloading generation data...')

    if zones == ['MEXICO (PAIS)']:
        query_string = """SELECT * FROM consumption_{} WHERE fecha >= '{}' AND fecha <= '{}'""".format(data, start_date, end_date)

    else:
        zones = ("','").join(zones)

        query_string = """SELECT * FROM consumption_{} WHERE fecha >= '{}' AND fecha <= '{}' AND zona_de_carga in ('{}')""".format(data, start_date, end_date, zones)


    SQL_for_file_output = "COPY ({}) TO STDOUT WITH CSV HEADER".format(query_string)

    file_name = get_download_file_name(f'consumption_{data}_{start_date[:10]}_{end_date[:10]}')

    file_path = f"..\\files\\descargas\\{file_name}"

    with open(file_path, 'w') as f:
        cursor.copy_expert(SQL_for_file_output, f)


def data_prices_download(cursor,start_date, end_date, market, zonas_nodos, zones, nodes):

    print('downloading prices data...')

    if not zones:
        return None

    queries = []
    if zonas_nodos == 'zones':

        zones = ("','").join(zones)
        for system in ['sin','bca','bcs']:

            queries.append("""SELECT * FROM {}_pnd_{} WHERE fecha >= '{}' AND fecha <= '{}' AND zona_de_carga in ('{}')""".format(system, market, start_date, end_date, zones))

    else:
        nodes = ("','").join(nodes)
        for system in ['sin','bca','bcs']:

            queries.append("""SELECT * FROM {}_pml_{} WHERE fecha >= '{}' AND fecha <= '{}' AND clave_nodo in ('{}')""".format(system, market, start_date, end_date, nodes))

    file_name = get_download_file_name(f'precios_{zonas_nodos}_{market}_{start_date[:10]}_{end_date[:10]}')
    file_path = f"..\\files\\descargas\\{file_name}"

    for i,query_string in enumerate(queries):
        if i == 0:
            SQL_for_file_output = "COPY ({}) TO STDOUT WITH CSV HEADER".format(query_string)

        else:
            SQL_for_file_output = "COPY ({}) TO STDOUT WITH CSV".format(query_string)

        with open(file_path, 'a') as f:
            cursor.copy_expert(SQL_for_file_output, f)


def data_SQL_download(cursor,query_string):

    print('requesting SQL data...')

    SQL_for_file_output = "COPY ({}) TO STDOUT WITH CSV HEADER".format(query_string)

    file_name = get_download_file_name('SQL_query')

    file_path = f"..\\files\\descargas\\{file_name}"

    with open(file_path, 'w') as f:
        cursor.copy_expert(SQL_for_file_output, f)



if __name__ == '__main__':

    db_name = 'cenace'

    conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
    cursor = conn.cursor()

    # fig = zones_prices(cursor, zones = ['OAXACA','PUEBLA','ORIZABA'])
    # fig.show()
    # print(prices_zones_table(cursor, system = 'sin', market = 'mda', zone = 'OAXACA', zones = [], price_component = 'precio_e'))
    # print(prices_nodes_table(cursor, system = 'sin', market = 'mtr', zona_de_carga='OAXACA', price_component='c_congestion'))




    conn.close()