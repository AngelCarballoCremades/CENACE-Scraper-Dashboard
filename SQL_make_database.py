# from io import StringIO
import os
import sys
import psycopg2 as pg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from functions import *

systems = ['BCA','BCS','SIN']
markets = ['MTR','MDA']
node_types = ['PND','PML']
energy_flows = ['generation','consumption']
data_types = ['forecast','real']
db_name = 'cenace'
folder_frame = '..\\files'

tables={}
tables['PND'] = (
    """CREATE TABLE IF NOT EXISTS {} (
    sistema VARCHAR(3),
    mercado VARCHAR(3),
    fecha DATE,
    hora SMALLINT,
    zona_de_carga VARCHAR(50),
    precio_e NUMERIC(7,2),
    c_energia NUMERIC(7,2),
    c_perdidas NUMERIC(7,2),
    c_congestion NUMERIC(7,2)
    );""")

tables['PML'] = (
    """CREATE TABLE  IF NOT EXISTS {} (
    sistema VARCHAR(3),
    mercado VARCHAR(3),
    fecha DATE,
    hora SMALLINT,
    clave_nodo VARCHAR(50),
    precio_e NUMERIC(8,2),
    c_energia NUMERIC(8,2),
    c_perdidas NUMERIC(8,2),
    c_congestion NUMERIC(8,2)
    );""")

tables['consumption_forecast'] = (
    """CREATE TABLE IF NOT EXISTS {} (
    sistema VARCHAR(3),
    zona_de_carga VARCHAR(50),
    fecha DATE,
    hora SMALLINT,
    energia NUMERIC(8,3)
    );""")

tables['consumption_real'] = (
    """CREATE TABLE IF NOT EXISTS {} (
    sistema VARCHAR(3),
    zona_de_carga VARCHAR(50),
    fecha DATE,
    hora SMALLINT,
    energia NUMERIC(8,3)
    );""")

tables['generation_forecast'] = (
    """CREATE TABLE IF NOT EXISTS {} (
    sistema VARCHAR(3),
    fecha DATE,
    hora SMALLINT,
    eolica NUMERIC(8,3),
    fotovoltaica NUMERIC(8,3)
    );""")

tables['generation_real'] = (
    """CREATE TABLE IF NOT EXISTS {} (
    sistema VARCHAR(3),
    fecha DATE,
    hora SMALLINT,
    eolica NUMERIC(8,3),
    fotovoltaica NUMERIC(8,3),
    biomasa NUMERIC(8,3),
    carboelectrica NUMERIC(8,3),
    ciclo_combinado NUMERIC(8,3),
    combustion_interna NUMERIC(8,3),
    geotermoelectrica NUMERIC(8,3),
    hidroelectrica NUMERIC(8,3),
    nucleoelectrica NUMERIC(8,3),
    termica_convencional NUMERIC(8,3),
    turbo_gas NUMERIC(8,3)
    );""")


def get_databases(cursor):

    cursor.execute("SELECT datname FROM pg_database;")
    return [db[0] for db in cursor.fetchall()]


def create_table(cursor, table, table_name):

    print('Creating table {}...'.format(table_name), end='')
    sys.stdout.flush()

    try:
        cursor.execute("DROP TABLE IF EXISTS {};".format(table_name.lower()))
        cursor.execute(table.format(table_name.lower()))
        print('Done')
    except:
        print("Failed creating table {}".format(table_name))


def main():

    # make_directory('files2')
    conn = pg2.connect(user='postgres', password=postgres_password())

    print('Making database.')

    # This is to allow creation of databases
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    databases = get_databases(cursor)

    print()

    if db_name in databases:
        print(f'Database {db_name} already exists.')
    else:
        cursor.execute("CREATE DATABASE {}".format(db_name))
        print(f'Database {db_name} created.')

    conn.commit()
    conn.close()

    print(f'Connecting to {db_name}...')

    conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
    cursor = conn.cursor()

    for energy_flow in energy_flows:
        for data_type in data_types:
            table_name = f'{energy_flow}_{data_type}'
            create_table(cursor = cursor,
                         table = tables[table_name],
                         table_name = table_name)

    for system in systems:
        for market in markets:
            for node in node_types:
                table_name = f'{system}_{node}_{market}'
                create_table(cursor = cursor,
                             table = tables[node],
                             table_name = table_name)

    for energy_flow in energy_flows:
        for data_type in data_types:
            table_name = f'{energy_flow}_{data_type}'
            upload_file_to_database(folder_frame, cursor, table_name)

    for system in systems:
        for market in markets:
            for node_type in node_types:
                table_name = f'{system}_{node_type}_{market}'
                upload_file_to_database(folder_frame, cursor, table_name)


    conn.commit()
    conn.close()

    for energy_flow in energy_flows:
        for data_type in data_types:
            subfolder = f'{energy_flow}\\{data_type}'
            delete_files(folder_frame, subfolder)


if __name__ == '__main__':
    main()