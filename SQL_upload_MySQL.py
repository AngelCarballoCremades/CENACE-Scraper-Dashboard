import mysql.connector


systems = ['BCA','BCS','SIN']
markets = ['MTR','MDA']
node_types = ['PND','PML']
db_name = 'cenace'



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
            "CREATE DATABASE IF NOT EXISTS {};".format(db_name))
    except:
        print("Failed creating database {}".format(db_name))


def create_table(cursor, table, system, market, node):
    table_name = f'{system}_{node}_{market}'


    print('Creating table {}'.format(table_name))
    try:
        cursor.execute(table.format(table_name))
    except:
        print("Failed creating table {}".format(table_name))


cnx = mysql.connector.connect(user='root', password='Licuadora1234', host='127.0.0.1')

cursor = cnx.cursor()

create_database(cursor, db_name)

try:
    cursor.execute("USE cenace;")
except:
    print("Error trying to use database {}.".format(DB_NAME))


for system in systems:
    for market in markets:
        for node in node_types:
            create_table(cursor=cursor, table=tables[node], system=system, market=market, node=node)


# cursor.execute("""LOAD DATA INFILE "BCA-PML-MDA.csv"
#     INTO TABLE bca_pml_mda
#     COLUMNS TERMINATED BY ','
#     LINES TERMINATED BY '\n'
#     IGNORE 1 LINES;""")



cnx.close()