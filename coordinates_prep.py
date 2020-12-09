import geopandas
import pandas as pd


gdf = geopandas.read_file('..\\inegi\\00mun.shp')
df = gdf[['CVEGEO','CVE_ENT','CVE_MUN','NOMGEO']]
df['LAT'] = gdf.centroid.to_crs(epsg = 4326).y
df['LON'] = gdf.centroid.to_crs(epsg = 4326).x
print(df)
print(df.dtypes)



folder_frame = 'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files'
db_name = 'cenace'


tables = {}
tables['nodes_info'] = (
    """CREATE TABLE IF NOT EXISTS {} (
    CVEGEO,
    CVE_ENT,
    CVE_MUN,
    NOMGEO
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
    # main()
    pass



