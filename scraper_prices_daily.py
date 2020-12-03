"""
Analiza la última fecha presente en los .csv creados con monthly_download.py y utiliza la API del cenace (https://www.cenace.gob.mx/DocsMEM/2020-01-14%20Manual%20T%C3%A9cnico%20SW-PEND.pdf) para actualizar la información a la última fecha disponible, actualiza los archivos .csv .
Falta agregar la API de PML (https://www.cenace.gob.mx/DocsMEM/2020-01-14%20Manual%20T%C3%A9cnico%20SW-PML.pdf), no se ha realizado por el peso de los archivos (supera los 2 GB en .csv), se requieren modificaciones menores ya que el método de invocación es prácticamente el mismo.
"""

import os
import sys
import time
import pandas as pd
import json
from datetime import date, timedelta

import psycopg2 as pg2

# import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed

from functions import *

# Data and system to be downloaded
systems = ['BCA','BCS','SIN']
node_types = ['PND','PML']
markets = ['MDA','MTR']

# APIs url
url_frame = {'PND':'https://ws01.cenace.gob.mx:8082/SWPEND/SIM/',
             'PML':'https://ws01.cenace.gob.mx:8082/SWPML/SIM/'} # Agregar al final los parámetros un '/'


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

    if days > 0:
        print(f'Last date on record is {last_date}, there are {days} days missing until {date_needed}.')

    return days, begining_date


def pack_nodes(raw_node_list, node_type):
    """Returns a list of lists with nodes, this is done because depending on node type we have a maximum number of nodes per request ()PND is 10 max and PML is 20 max. PML missing"""
    node_list = [node[0].replace(' ','-') for node in raw_node_list]

    size_limit = 10 if node_type == 'PND' else 20

    nodes_api = []
    while True:
        if len(node_list) > size_limit:
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


def get_urls_to_request(nodes_packed, dates, system, node_type, market):

    urls_list = []
    for node_group in nodes_packed:
        nodes_string = ','.join(node_group)

        # Select correct API base
        url = url_frame[node_type]

        # Building request url with data provided
        url_complete = f'{url}{system}/{market}/{nodes_string}/{dates[0][:4]}/{dates[0][5:7]}/{dates[0][8:]}/{dates[1][:4]}/{dates[1][5:7]}/{dates[1][8:]}/JSON'

        urls_list.append(url_complete)

    return urls_list


def check_data(json_data, date_interval):

    if json_data['status'] == 'OK':

        first_date = json_data['Resultados'][0]['Valores'][0]['fecha']
        last_date = json_data['Resultados'][0]['Valores'][-1]['fecha']

        if [first_date,last_date] != date_interval:
            print(f'---Got data up to {last_date}, missing {date_interval[1]}---')

        return True

    else:
        if json_data['status'] == 'ZERO RESULTS':
            print(f'---No data availabe for dates {first_date} to {last_date}---')
        else:
            print(f"---Data status not 'OK': {json_data['status']}---")

        return False


def json_to_dataframe(json_file):
    """Reads json file, creates a list of nodes DataFrames and concatenates them. After that it cleans/orders the final df and returns it"""
    dfs = []

    for node in json_file['Resultados']:
        dfs.append(pd.DataFrame(node))

    df = pd.concat(dfs) # Join all data frames

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



def main():

    conn = pg2.connect(user='postgres', password=postgres_password(), database='cenace')
    cursor = conn.cursor()
    session = FuturesSession(max_workers=20)

    for node_type in node_types:
        for system in systems:

            print(f'{system}-{node_type}')
            print('Getting list of nodes...')

            # Node list to upload from sql database
            nodes = get_unique_nodes(cursor, system, node_type)

            # Prepare nodes for API requests
            nodes_packed = pack_nodes(nodes, node_type)

            for market in markets:

                print(f'{market} - Looking for last date...')

                last_date = get_last_date(cursor, system, node_type, market)
                days, begining_date = missing_dates(last_date, market)
                dates_packed = pack_dates(days, begining_date)

                if len(dates_packed):

                    valid_values = True

                    for date_interval in dates_packed:

                        urls_list = get_urls_to_request(nodes_packed, date_interval, system, node_type, market)

                        print(f'{len(urls_list)} Requests', end='')
                        sys.stdout.flush()

                        futures=[session.get(u) for u in urls_list]

                        dfs = [] # List of missing info data frames

                        for future in as_completed(futures):

                            resp = future.result()
                            json_data = resp.json()
                            valid_values = check_data(json_data, date_interval)

                            if not valid_values:
                                break

                            dfs.append(json_to_dataframe(json_data))
                            print('.', end='')
                            sys.stdout.flush()

                        if not valid_values:
                            break

                        print('Done')

                        df = pd.concat(dfs) # Join downloaded info in one data frame

                        values = pack_values(df)

                        print(f'Uploading data from {date_interval[0]} to {date_interval[1]}', end='')
                        sys.stdout.flush()

                        insert_into_table(cursor, system, node_type, market, values)

                        conn.commit()

                    print(f'{system}-{node_type}-{market} up to date\n')

                #If there are no updates to be made...
                else:
                    print(f'{system}-{node_type}-{market} up to date\n')

    print('.....................DONE.....................')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()