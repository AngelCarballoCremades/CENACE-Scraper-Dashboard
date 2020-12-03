import os
import sys
import psycopg2 as pg2
from functions import *
import scraper_prices_daily
import

energy_flows = ['generation','consumption']
data_types = ['forecast','real']
db_name = 'cenace'

def get_last_date(cursor, table_name):

    cursor.execute("SELECT MAX(fecha) FROM {};".format(table_name))
    return cursor.fetchall()

def main():
    # scraper_prices_daily.main()

    conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
    cursor = conn.cursor()

    for energy_flow in energy_flows:
        for data_type in data_types:

            table_name = f'{energy_flow}_{data_type}'
            print(table_name, end=':  ')

            last_date = get_last_date(cursor, table_name)
            print(last_date[0][0])



if __name__ == '__main__':
    main()

