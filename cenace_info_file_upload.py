import pandas as pd
import psycopg2 as pg2
import os
from functions import *

folder_frame = 'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files'
db_name = 'cenace'


tables = {}
tables['nodes_info'] = (
    """CREATE TABLE IF NOT EXISTS {} (
    sistema VARCHAR(3),
    centro_de_control_regional VARCHAR(200),
    zona_de_carga VARCHAR(50),
    clave_nodo VARCHAR(10),
    nombre_nodo VARCHAR(200),
    nodop_nivel_de_tensión_kv VARCHAR(7),
    tipo_de_carga_directamente_modelada VARCHAR(100),
    tipo_de_carga_indirectamente_modelada VARCHAR(100),
    tipo_de_generación_directamente_modelada VARCHAR(100),
    tipo_de_generación_indirectamente_modelada VARCHAR(100),
    transmisión_zona_de_operación_de_transmisión VARCHAR(200),
    transmisión_gerencia_regional_de_transmisión VARCHAR(200),
    distribución_zona_de_distribución VARCHAR(200),
    distribución_gerencia_divisional_de_distribución VARCHAR(200),
    ubicación_clave_de_entidad_federativa VARCHAR(9),
    ubicación_entidad_federativa VARCHAR(200),
    ubicación_clave_de_municipio VARCHAR(9),
    ubicación_municipio VARCHAR(200),
    prodesen_region_de_transmision VARCHAR(200)
    );""")


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



    file = [file for file in os.listdir('..\\docs') if file[-4:] == 'xlsx'][0]

    df = pd.read_excel(f'..\\docs\\{file}', header=[0,1])
    df.columns = [' '.join(col) if 'Unnamed' not in col[0] else col[1] for col in df.columns.values]
    for col in df.columns:
        print(col.lower().replace(' ','_'))#, 'VARCHAR(200),')

    df.to_csv(f'{folder_frame}\\nodes_info.csv', index = False, header = False, sep='\t')


    print(f'Connecting to {db_name}...')

    conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
    cursor = conn.cursor()

    table_name = f'nodes_info'
    create_table(cursor = cursor,
                 table = tables[table_name],
                 table_name = table_name)

    upload_file_to_database(folder_frame, cursor, table_name, sep = '\t')

    conn.commit()

    # cursor.execute("""SELECT * FROM nodes_info limit 10;""")

    # print(cursor.fetchall())





    conn.close()

if __name__ == '__main__':
    main()