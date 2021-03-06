import os
import sys
import psycopg2 as pg2
from functions import *
import scraper_prices_daily
import scraper_generation_real
import scraper_generation_forecast
import scraper_consumption

import join_files_generation_real
import join_files_generation_forecast
import join_files_consumption_real
import join_files_consumption_forecast


energy_flows = ['generation','consumption']
data_types = ['forecast','real']
systems = ['BCA','BCS','SIN']
markets = ['MTR','MDA']
node_types = ['PND','PML']
db_name = 'cenace'


def get_last_date(cursor, table_name):

    cursor.execute("SELECT MAX(fecha) FROM {};".format(table_name))
    return cursor.fetchall()

def rebuild_table_index(cursor, table_name):

    print('Rebuilding index on table {}...'.format(table_name), end='')
    sys.stdout.flush()

    try:
        cursor.execute("""REINDEX TABLE {};""".format(table_name))
        print('Done')
    except:
        print('Failed')


def main():

    scraper_prices_daily.main()

    conn = pg2.connect(**postgres_password(), database=db_name)
    cursor = conn.cursor()

    for energy_flow in energy_flows:
        for data_type in data_types:

            keep_going = True
            table_name = f'{energy_flow}_{data_type}'
            last_date = get_last_date(cursor, table_name)[0][0]

            if table_name == 'generation_real':
                keep_going = scraper_generation_real.main(last_month = last_date.month, last_year = last_date.year)

            if table_name == 'generation_forecast':
                keep_going = scraper_generation_forecast.main(last_date = last_date.strftime('%Y-%m-%d'))

            if table_name == 'consumption_real':
                keep_going = scraper_consumption.main(last_date = last_date.strftime('%Y-%m-%d'), data_type = 'real')

            if table_name == 'consumption_forecast':
                keep_going = scraper_consumption.main(last_date = last_date.strftime('%Y-%m-%d'), data_type = 'forecast')

            if not keep_going:
                continue

            if table_name == 'generation_real':
                join_files_generation_real.main()

            if table_name == 'generation_forecast':
                join_files_generation_forecast.main()

            if table_name == 'consumption_real':
                join_files_consumption_real.main()

            if table_name == 'consumption_forecast':
                join_files_consumption_forecast.main()

            upload_file_to_database(get_path(), cursor, table_name)
            conn.commit()

            delete_files(get_path(a = energy_flow, b = data_type))

    for system in systems:
        for market in markets:
            for node_type in node_types:
                table_name = f'{system}_{node_type}_{market}'
                rebuild_table_index(cursor, table_name)

    conn.close()

    print("------------Update Done---------------")

if __name__ == '__main__':
    main()

