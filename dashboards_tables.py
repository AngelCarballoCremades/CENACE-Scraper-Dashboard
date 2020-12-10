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

    print(df_nodes.T)
    print(df_zone.T)
    print(df.T)


    return df







if __name__ == '__main__':

    db_name = 'cenace'

    conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
    cursor = conn.cursor()

    # fig = zones_prices(cursor, zones = ['OAXACA','PUEBLA','ORIZABA'])
    # fig.show()
    # print(prices_zones_table(cursor, system = 'sin', market = 'mda', zone = 'OAXACA', zones = [], price_component = 'precio_e'))
    print(prices_nodes_table(cursor, system = 'sin', market = 'mtr', zona_de_carga='OAXACA', price_component='c_congestion'))
    conn.close()