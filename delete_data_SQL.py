"""
Analiza la última fecha presente en los .csv creados con monthly_download.py y utiliza la API del cenace (https://www.cenace.gob.mx/DocsMEM/2020-01-14%20Manual%20T%C3%A9cnico%20SW-PEND.pdf) para actualizar la información a la última fecha disponible, actualiza los archivos .csv .
Falta agregar la API de PML (https://www.cenace.gob.mx/DocsMEM/2020-01-14%20Manual%20T%C3%A9cnico%20SW-PML.pdf), no se ha realizado por el peso de los archivos (supera los 2 GB en .csv), se requieren modificaciones menores ya que el método de invocación es prácticamente el mismo.
"""

import os
import sys
import pdb
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import date, timedelta
import json
import psycopg2 as pg2
import grequests

# Data and system to be downloaded
datas = ['PND-MTR','PND-MDA']#,'PML-MTR','PML-MDA']
systems = ['BCA','BCS','SIN']
node_types = ['PND','PML']
markets = ['MDA','MTR']

# APIs url
url_frame = {}
url_frame['PND'] = 'https://ws01.cenace.gob.mx:8082/SWPEND/SIM/' # Agregar al final los parámetros un '/'
url_frame['PML'] = 'https://ws01.cenace.gob.mx:8082/SWPML/SIM/' # Agregar al final los parámetros un '/'


def get_unique_nodes(cursor, system, node_type, market = 'MTR'):

    table_name = '{}_{}_{}'.format(system, node_type, market)

    if node_type == 'PML':
        node_column = 'clave_nodo'
    elif node_type == 'PND':
        node_column = 'zona_de_carga'

    cursor.execute("""SELECT {} FROM {}
            WHERE fecha = (SELECT MAX(fecha) FROM {}) AND
            hora = 24;""".format(node_column, table_name, table_name))

    return cursor.fetchall()


def get_last_date(cursor, system, node_type, market):

    cursor.execute("""SELECT MAX(fecha) FROM {}_{}_{};""".format(system, node_type, market))
    return cursor.fetchall()[0][0]


def get_url(nodes, dates, system, node_type, market):

    # Building node string
    nodes_string = ','.join(nodes)

    # Select correct API base
    url = url_frame[node_type]

    # Building request url with data provided
    url_complete = f'{url}{system}/{market}/{nodes_string}/{dates[0][:4]}/{dates[0][5:7]}/{dates[0][8:]}/{dates[1][:4]}/{dates[1][5:7]}/{dates[1][8:]}/JSON'

    # print('Requesting...', end='')
    # sys.stdout.flush()

    # req = requests.get(url_complete)

    # if req.status_code != 200:
    #     print(req.status_code)
    #     print("Requesting again...", end='')
    #     sys.stdout.flush()

    #     req = requests.get(url_complete)
    #     if req.status_code != 200:
    #         print(req.status_code)
    #         sys.stdout.flush()
    #         raise

    # print('Processing...', end='')
    # sys.stdout.flush()


    # soup = BeautifulSoup(req.content, 'html.parser')
    # print('json')
    # json_data = json.loads(req.json())
    # print(json_data)

    return url_complete


def check_data(json_data, date_interval):
    if json_data['status'] == 'OK':

        first_date = json_data['Resultados'][0]['Valores'][0]['fecha']
        last_date = json_data['Resultados'][0]['Valores'][-1]['fecha']

        if [first_date,last_date] != date_interval:
            print('')
            print(f'Dates requested: {date_interval[0]} - {date_interval[1]}')
            print(f'Dates obtained: {first_date} - {last_date}')

    else:
        print()
        print(f"Data status not 'OK': {json_data['status']}")
        print(json_data)


def missing_dates(last_date, market):
    """Returns begining date to ask info for depending on df's last date detected and type of market, also returns days of info to be asked for"""
    today = date.today()

    begining_date = last_date + timedelta(days = 1) # Date to start asking for (last_date plus 1 day)

    # MDA is available from today +1
    if market == 'MDA':
        date_needed = today + timedelta(days = 1)

    # MTR is available from today -7
    elif market == 'MTR':
        date_needed = today - timedelta(days = 7)

    days = (date_needed - last_date).days # Total days needed to update

    print(f'{system}-{node_type}-{market} Last date on record is {last_date}, there are {days} days missing until {date_needed}.')
    return days, begining_date

def pack_nodes(raw_node_list, node_type):
    """Returns a list of lists with nodes, this is done because depending on node type we have a maximum number of nodes per request ()PND is 10 max and PML is 20 max. PML missing"""
    node_list = [node[0].replace(' ','-') for node in raw_node_list]

    size_limit = 10 if node_type == 'PND' else 20

    nodes_api = []
    while True:
        if len(node_list) >= size_limit:
            nodes_api.append(node_list[:size_limit])
            node_list = node_list[size_limit:]
        else:
            nodes_api.append(node_list)
            break

    return nodes_api

def pack_dates(days, begining_date):
    """Gets days to ask for info and start date, returns appropiate data intervals to assemble APIs url"""
    dates = []
    start_date = begining_date

    while days > 0:

        if days >= 7:
            end_date = start_date + timedelta(days = 6)
            dates.append( [str(start_date),str(end_date)] )
            start_date = end_date + timedelta(days = 1)
            days -= 7

        else:
            end_date = start_date + timedelta(days = days -1)
            dates.append( [str(start_date),str(end_date)] )
            days = 0

    return dates


def json_to_dataframe(json_file):
    """Reads json file, creates a list of nodes DataFrames and concatenates them. After that it cleans/orders the final df and returns it"""
    dfs = []

    for node in json_file['Resultados']:
        dfs.append(pd.DataFrame(node))
        # print(node)

    df = pd.concat(dfs) # Join all data frames

    # print(df)
    # Clean/order df to same format of existing csv files
    df['sistema'] = json_file['sistema']
    df['mercado'] = json_file['proceso']
    df['fecha'] = df['Valores'].apply(lambda x: x['fecha'])
    df['hora'] = df['Valores'].apply(lambda x: x['hora'])

    if json_file['nombre'] == 'PEND':
        df['precio_e'] = df['Valores'].apply(lambda x: x['pz'])
        df['c_energia'] = df['Valores'].apply(lambda x: x['pz_ene'])
        df['c_perdidas'] = df['Valores'].apply(lambda x: x['pz_per'])
        df['c_congestion'] = df['Valores'].apply(lambda x: x['pz_cng'])
        df['zona_de_carga'] = df['zona_carga'].copy()
        df = df[['sistema','mercado','fecha','hora','zona_de_carga','precio_e','c_energia', 'c_perdidas','c_congestion']]

    if json_file['nombre'] == 'PML':
        df['precio_e'] = df['Valores'].apply(lambda x: x['pml'])
        df['c_energia'] = df['Valores'].apply(lambda x: x['pml_ene'])
        df['c_perdidas'] = df['Valores'].apply(lambda x: x['pml_per'])
        df['c_congestion'] = df['Valores'].apply(lambda x: x['pml_cng'])
        df['clave_nodo'] = df['clv_nodo'].copy()
        df = df[['sistema','mercado','fecha','hora','clave_nodo','precio_e','c_energia', 'c_perdidas','c_congestion']]

    # print(df)
    return df

def pack_values(df):

    large_list = []
    small_list = []
    for row in df.values.tolist():
        row[0] = f"'{row[0]}'"
        row[1] = f"'{row[1]}'"
        row[2] = f"'{row[2]}'"
        row[4] = f"'{row[4]}'"

        small_list.append(','.join(row))

        if len(small_list) == 1000:
            large_list.append(f"({'),('.join(small_list)})")
            small_list = []


    if not large_list:
        large_list.append(f"({'),('.join(small_list)})")
        small_list = []

    return large_list


def insert_into_table(cursor, system, node_type, market, values):

    for i in range(len(values)):
        print('.', end='')
        sys.stdout.flush()

        cursor.execute("""INSERT INTO {}_{}_{} VALUES {};""".format(system.lower(), node_type.lower(), market.lower(), values[i]))

    print('Done.')




conn = pg2.connect(user='postgres', password='Licuadora1234', database='cenace')
cursor = conn.cursor()


for node_type in node_types:
    for system in systems:

        # Node list to upload from sql database
        nodes = get_unique_nodes(cursor, system, node_type)

        # Prepare nodes for API requests
        nodes_packed = pack_nodes(nodes, node_type)

        for market in markets:


            last_date = get_last_date(cursor, system, node_type, market)
            days, begining_date = missing_dates(last_date, market)
            dates_packed = pack_dates(days, begining_date)

            if len(dates_packed):

                total_requests = len(nodes_packed) * len(dates_packed)

                i = 1
                for date_interval in dates_packed:

                    dfs = [] # List of missing info data frames
                    urls_to_get = []

                    for node_group in nodes_packed:

                        # print(f'{i}/{total_requests} ', end='')
                        # sys.stdout.flush()

                        urls_to_get.append(get_url(node_group, date_interval, system, node_type, market))

                        # check_data(json_data, date_interval)

                        # print('Appending...', end='')
                        # sys.stdout.flush()

                        # dfs.append(json_to_dataframe(json_data))
                        # print('Done.')

                        i += 1

                    rs = (grequests.get(u) for u in urls_to_get)

                    reqs = grequests.map(rs)

                    print(reqs)



#                     df = pd.concat(dfs) # Join downloaded info in one data frame

#                     values = pack_values(df)
#                     # print(values)

#                     print(f'Uploading data from {date_interval[0]} to {date_interval[1]} into SQL database.', end='')
#                     sys.stdout.flush()
#                     insert_into_table(cursor, system, node_type, market, values)

#                         # break
#     #                 break
#     #         break
#     #     break
#     # break


#                     conn.commit()

#                 print(f'{system}-{node_type}-{market} up to date\n')

#              #If there are no updates to be made...
#             else:
#                 print(f'{system}-{node_type}-{market} up to date\n')

# print('.....................DONE.....................')

# # conn.commit()
# # conn.close()
