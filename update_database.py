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
db_name = 'cenace'
folder = '..\\files'


def get_last_date(cursor, table_name):

    cursor.execute("SELECT MAX(fecha) FROM {};".format(table_name))
    return cursor.fetchall()

def main():

    scraper_prices_daily.main()

    conn = pg2.connect(user='postgres', password=postgres_password(), database=db_name)
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

            upload_file_to_database(folder, cursor, table_name)
            conn.commit()

            delete_files(folder, subfolder = f'{energy_flow}\\{data_type}')

    conn.close()

if __name__ == '__main__':
    main()

