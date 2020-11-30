import psycopg2 as pg2
from io import StringIO
import os

systems = ['BCA','BCS','SIN']
markets = ['MTR','MDA']
node_types = ['PND','PML']
db_name = 'cenace'

folder_frame = 'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files'

tables = {}

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

def create_database(cursor, db_name):

    try:
        cursor.execute(
            "CREATE DATABASE {};".format(db_name))
    except:
        print("Failed creating database {}".format(db_name))


def create_table(cursor, table, system, market, node):

    table_name = f'{system}_{node}_{market}'
    print('Creating table {}'.format(table_name))

    try:
        cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))
        cursor.execute(table.format(table_name))
    except:
        print("Failed creating table {}".format(table_name))


def upload_file_to_database(system, node, market):

    files = get_files_names(system, node, market)
    table = f"{system}_{node}_{market}"

    for file in files:
        print(f"Uploading {file} to table {table}")
        file_path = f"{folder_frame}\\{file}"

        with open(file_path, 'rb') as f:
            cursor.copy_from(f, table, sep=',')


def get_files_names(system, node, market):
    """This function returns folder,files wher folder is the folder to look for files in the selected system and data, files is a list with the name of all the files available"""
    files_list = os.listdir(folder_frame)
    files = [file for file in files_list if (system in file and node in file and market in file)]
    return files


conn = pg2.connect(user='postgres', password='Licuadora1234', database='cenace')

cursor = conn.cursor()


for system in systems:
    for market in markets:
        for node in node_types:
            create_table(cursor=cursor, table=tables[node], system=system, market=market, node=node)


for system in systems:
    for market in markets:
        for node in node_types:
            upload_file_to_database(system, node, market)

conn.commit()
conn.close()