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

# Data and system to be downloaded
datas = ['PND-MTR','PND-MDA']#,'PML-MTR','PML-MDA']
systems = ['BCA','BCS','SIN']

# APIs url
url_frame = f'https://ws01.cenace.gob.mx:8082/SWPEND/SIM/' # Agregar al final los parámetros un '/'

def file_path(data,system):
    """Returns systems and data specific csv's file path """
    file = f'C:\\Users\\Angel\\Documents\\Ironhack\\web_project\\files\\{system}-{data}.csv'
    return file

def get_json(nodes, dates, system, data):
    """Builds APIs request url, requests it, process the result and returns a clean json string"""
    nodes_string = ''

    # Building node string
    for node in nodes:
        nodes_string += f'{node},'

    nodes_string = nodes_string[:-1]

    # Building request url with data provided
    url_complete = f'{url_frame}{system}/{data[-3:]}/{nodes_string}/{dates[0][:4]}/{dates[0][5:7]}/{dates[0][8:]}/{dates[1][:4]}/{dates[1][5:7]}/{dates[1][8:]}/JSON'

    req = requests.get(url_complete)
    soup = BeautifulSoup(req.content, 'html.parser')
    json_file = json.loads(str(soup.text))

    return json_file

def missing_dates(df):
    """Returns begining date to ask info for depending on df's last date detected and type of market, also returns days of info to be asked for"""
    today = date.today()
    last_date = df['Fecha'].max() # Last date on record

    # Getting last date in correct format to work with it
    year = int(last_date[:4])
    month = int(last_date[5:7])
    day = int(last_date[8:])
    last_date = date(year, month, day)

    begining_date = last_date + timedelta(days = 1) # Date to start asking for (last_date plus 1 day)

    # MDA is available from today +1
    if data[-3:] == 'MDA':
        date_needed = today + timedelta(days = 1)

    # MTR is available from today -7
    elif data[-3:] == 'MTR':
        date_needed = today - timedelta(days = 7)

    days = (date_needed - last_date).days # Total days needed to update

    print(f'{system}-{data} Last date on record is {last_date}, there are {days} days missing until {date_needed}.')
    return days, begining_date

def get_nodes_api(nodes):
    """Returns a list of lists with nodes, this is done because depending on node type we have a maximum number of nodes per request ()PND is 10 max and PML is 20 max. PML missing"""
    nodes_api = []
    while True:
        if len(nodes) >= 10:
            nodes_api.append(nodes[:10])
            nodes = nodes[10:]
        else:
            nodes_api.append(nodes)
            break

    return nodes_api

def dates_intervals(days, begining_date):
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

def get_data_frame(json_file):
    """Reads json file, creates a list of nodes DataFrames and concatenates them. After that it cleans/orders the final df and returns it"""
    dfs = []
    for node in json_file['Resultados']:
        dfs.append(pd.DataFrame(node))

    df = pd.concat(dfs) # Join all data frames

    # Clean/order df to same format of existing csv files
    df['Fecha'] = df['Valores'].apply(lambda x: x['fecha'])
    df['Hora'] = df['Valores'].apply(lambda x: x['hora'])
    df['Precio Zonal  ($/MWh)'] = df['Valores'].apply(lambda x: x['pz'])
    df['Componente energia  ($/MWh)'] = df['Valores'].apply(lambda x: x['pz_ene'])
    df['Componente perdidas  ($/MWh)'] = df['Valores'].apply(lambda x: x['pz_per'])
    df['Componente Congestion  ($/MWh)'] = df['Valores'].apply(lambda x: x['pz_cng'])

    df['Zona de Carga'] = df['zona_carga'].copy()

    df = df[['Fecha', 'Hora', 'Zona de Carga', 'Precio Zonal  ($/MWh)',
           'Componente energia  ($/MWh)', 'Componente perdidas  ($/MWh)',
           'Componente Congestion  ($/MWh)']]
    return(df)


# Main code
for system in systems:
    for data in datas:

        df = pd.read_csv(file_path(data,system)) # Reads system and data existing file

        nodes = [node.replace(' ', '-') for node in df['Zona de Carga'].unique().tolist()] # Unique list of nodes in system file

        nodes_api = get_nodes_api(nodes) # Prepares nodes for requests

        days,begining_date = missing_dates(df) # Gets number of missing dates in info

        dates = dates_intervals(days, begining_date) # Prepares dates for requests

        # If there are updates to be made...
        if len(dates):
            requests_left = len(nodes_api) * len(dates)
            dfs = [] # List of missing info data frames

            for node_group in nodes_api:

                for date_interval in dates:

                    print(f'{requests_left} requests left.')
                    json_file = get_json(node_group,date_interval,system,data) # Request and get json with data
                    dfs.append(get_data_frame(json_file)) # Add new requested info to main data frame
                    requests_left -= 1

            df = pd.concat(dfs) # Join downloaded info in one data frame
            df_prev = pd.read_csv(f'{file_path(data,system)}') # Get existing info file

            df_final = pd.concat([df_prev,df]) # Join existing info with downloaded info

            # Order new data frame
            df_final.sort_values(by = ['Zona de Carga','Fecha','Hora'], inplace = True ,ascending = [True,True,True])

            # Overwrite existing file with updated file
            df_final.to_csv(f'{file_path(data,system)}', index = False)
            print(f'{system}-{data} up to date\n')

        #  If there are no updates to be made...
        else:
            print(f'{system}-{data} up to date\n')

print('.....................DONE.....................')