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
        try:
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
        except:
            cursor.execute("ROLLBACK")
            pass

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
        try:
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
        except:
            cursor.execute("ROLLBACK")
            pass

        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
        dfs.append(df)

    df_data = pd.concat(dfs)
    df_data[['precio_maximo', 'precio_minimo', 'precio_promedio', 'desviacion_estandar']] = df_data[['precio_maximo', 'precio_minimo', 'precio_promedio', 'desviacion_estandar']].astype('float').round(2)

    df = pd.merge(left = df_nodos, right = df_data, on='clave_nodo')

    return df


def prices_zones_table(cursor, market, zone, zones, price_component):

    if not zones:
        zones = [zone]

    if zone in zones:
        pass
    else:
        zones.append(zone)

    zones = "','".join(zones)
    year = datetime.datetime.now().year

    print(f'requesting zones table...')

    dfs = []
    for system in ['sin','bca','bcs']:
        try:
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
        except:
            cursor.execute("ROLLBACK")
            pass

        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
        dfs.append(df)

    df = pd.concat(dfs)

    for col in df.columns:
        if col != 'zona_de_carga':
            df[col] = df[col].astype('float').round(2)

    return df


def prices_nodes_table(cursor, market, zona_de_carga, price_component):

    year = datetime.datetime.now().year

    print('requesting nodes prices...')
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

    try:
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
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df_nodes = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    print('...')
    try:
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
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df_zone = pd.DataFrame(data=cursor.fetchall(), columns=colnames)


    df = pd.concat([df_zone, df_nodes])


    for col in df.columns:
        if col != 'clave_nodo':
            df[col] = df[col].astype('float').round(2)

    return df


def data_generation_preview(cursor,start_date, end_date, data):

    print('requesting generation data...')

    try:
        cursor.execute("""
            SELECT * FROM generation_{}
            WHERE
                fecha >= '{}' AND
                fecha <= '{}'
            ORDER BY fecha ASC, hora ASC
            LIMIT 50
            ;""".format(data, start_date, end_date))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    for col in df.columns:
        if col not in ['sistema','fecha','hora']:
            df[col] = df[col].astype('float').round(2)

    return df


def data_consumption_preview(cursor,start_date, end_date, data, zones):

    print('requesting consumption data...')

    if zones == ['MEXICO (PAIS)']:
        try:
            cursor.execute("""
                SELECT * FROM consumption_{}
                WHERE
                    fecha >= '{}' AND
                    fecha <= '{}'
                ORDER BY
                    sistema ASC,
                    zona_de_carga ASC,
                    fecha ASC,
                    hora ASC
                LIMIT 50
                ;""".format(data, start_date, end_date))
        except:
            cursor.execute("ROLLBACK")
            pass

    else:
        zones = ("','").join(zones)

        try:
            cursor.execute("""
                SELECT * FROM consumption_{}
                WHERE
                    fecha >= '{}' AND
                    fecha <= '{}' AND
                    zona_de_carga in ('{}')
                ORDER BY
                    sistema ASC,
                    zona_de_carga ASC,
                    fecha ASC,
                    hora ASC
                LIMIT 50
                ;""".format(data, start_date, end_date, zones))
        except:
            cursor.execute("ROLLBACK")
            pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
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

            try:
                cursor.execute("""
                    SELECT * FROM {}_pnd_{}
                    WHERE
                        fecha >= '{}' AND
                        fecha <= '{}' AND
                        zona_de_carga in ('{}')
                    ORDER BY
                        sistema ASC,
                        zona_de_carga ASC,
                        fecha ASC,
                        hora ASC
                    LIMIT 30
                    ;""".format(system, market, start_date, end_date, zones))
            except:
                cursor.execute("ROLLBACK")
                pass

            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
            dfs.append(df)

        df = pd.concat(dfs)
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
                ORDER BY
                    sistema ASC,
                    clave_nodo ASC,
                    fecha ASC,
                    hora ASC
                LIMIT 30;""".format(system, market, start_date, end_date, nodes))


            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
            dfs.append(df)

        df = pd.concat(dfs)
        return df


def data_generation_download(cursor, start_date, end_date, data):

    print('downloading generation data...')

    try:
        cursor.execute("""
            SELECT * FROM generation_{}
            WHERE
                fecha >= '{}' AND
                fecha <= '{}'
            ORDER BY
                fecha ASC,
                hora ASC
            ;""".format(data, start_date, end_date))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    for col in df.columns:
        if col not in ['sistema','fecha','hora']:
            df[col] = df[col].astype('float').round(2)

    return df


def data_consumption_download(cursor,start_date, end_date, data, zones):

    print('downloading generation data...')

    if zones == ['MEXICO (PAIS)']:
        try:
            cursor.execute("""
                SELECT * FROM consumption_{}
                WHERE
                    fecha >= '{}' AND
                    fecha <= '{}'
                ORDER BY
                    sistema ASC,
                    zona_de_carga ASC,
                    fecha ASC,
                    hora ASC
                ;""".format(data, start_date, end_date))
        except:
            cursor.execute("ROLLBACK")
            pass

    else:
        zones = ("','").join(zones)

        try:
            cursor.execute("""
                SELECT * FROM consumption_{}
                WHERE
                    fecha >= '{}' AND
                    fecha <= '{}' AND
                    zona_de_carga in ('{}')
                ORDER BY
                    sistema ASC,
                    zona_de_carga ASC,
                    fecha ASC,
                    hora ASC
                ;""".format(data, start_date, end_date, zones))
        except:
            cursor.execute("ROLLBACK")
            pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
    df['energia'] = df['energia'].astype('float')

    return df


def data_prices_download(cursor,start_date, end_date, market, zonas_nodos, zones, nodes):

    print('downloading prices data...')

    if not zones:
        return pd.DataFrame()

    dfs = []

    if zonas_nodos == 'zones':

        zones = ("','").join(zones)

        for system in ['sin','bca','bcs']:

            try:
                cursor.execute("""
                    SELECT * FROM {}_pnd_{}
                    WHERE
                        fecha >= '{}' AND
                        fecha <= '{}' AND
                        zona_de_carga in ('{}')
                    ORDER BY
                        sistema ASC,
                        zona_de_carga ASC,
                        fecha ASC,
                        hora ASC
                    ;""".format(system, market, start_date, end_date, zones))
            except:
                cursor.execute("ROLLBACK")
                pass

            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
            dfs.append(df)

        df = pd.concat(dfs)
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
                ORDER BY
                    sistema ASC,
                    clave_nodo ASC,
                    fecha ASC,
                    hora ASC
                ;""".format(system, market, start_date, end_date, nodes))


            colnames = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)
            dfs.append(df)

        df = pd.concat(dfs)
        return df


def data_nodesinfo_region(cursor,regiones):

    print('requesting nodes_info regiones data...')

    regiones = ("','").join(regiones)

    try:
        cursor.execute("""
            SELECT * FROM nodes_info
            WHERE
                centro_de_control_regional IN ('{}')
            ORDER BY
                centro_de_control_regional ASC,
                zona_de_carga ASC,
                clave_nodo ASC
            ;""".format(regiones))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    return df

def data_nodesinfo_zone(cursor,zones):

    print('requesting nodes_info zones data...')

    zones = ("','").join(zones)

    try:
        cursor.execute("""
            SELECT * FROM nodes_info
            WHERE
                zona_de_carga IN ('{}')
            ORDER BY
                centro_de_control_regional ASC,
                zona_de_carga ASC,
                clave_nodo ASC
            ;""".format(zones))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    return df

def data_nodesinfo_node(cursor,nodes):

    print('requesting nodes_info nodes data...')

    nodes = ("','").join(nodes)

    try:
        cursor.execute("""
            SELECT * FROM nodes_info
            WHERE
                clave_nodo IN ('{}')
            ORDER BY
                centro_de_control_regional ASC,
                zona_de_carga ASC,
                clave_nodo ASC
            ;""".format(nodes))
    except:
        cursor.execute("ROLLBACK")
        pass

    colnames = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data=cursor.fetchall(), columns=colnames)

    return df


if __name__ == '__main__':
    pass